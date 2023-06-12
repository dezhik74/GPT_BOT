import os
import re
import time
from datetime import datetime
from tempfile import NamedTemporaryFile

from aiogram import Bot, Dispatcher, executor, types

import logging

import openai
from aiogram.types import ContentType
from openai import APIError
from openai.error import RateLimitError, APIConnectionError, InvalidRequestError, AuthenticationError, \
    ServiceUnavailableError, Timeout
from pydub import AudioSegment

from gpt_bot.dialogs import Dialogs
from gpt_bot.main_keyboard import get_main_kb
from gpt_bot import settings
from gpt_bot.templates import render_template

# settings logging
if settings.IN_DOCKER:
    logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a')
else:
    logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=settings.TELEGA_TOKEN)
dp = Dispatcher(bot)
openai.api_key = settings.OPENAI_API_TOKEN
dialogs = Dialogs()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    m = render_template('help.j2', {'in_docker': settings.IN_DOCKER})
    await message.reply(m, reply_markup=get_main_kb(message.from_user.id))

@dp.message_handler(commands=['st', 'status'])
async def send_status(message: types.Message):
    d = dialogs.get_dialog(message.from_user.id)
    if d is None:
        await message.reply(render_template('not_dialog.j2', {'user_id': message.from_user.id}))
    else:
        if not settings.IN_DOCKER:
            print('---------------------------')
            for replica in d.messages:
                print('role: ', replica.role)
                print('message: ', replica.content)
                print('tokens: ', replica.tokens_num)
                print('---------------------------')
        await message.reply(render_template('status.j2', {
            'user_id': message.from_user.id,
            'total_tokens': d.total_tokens_num(),
            'total_replies': len(d)
        }))

@dp.message_handler(commands=['clear'])
async def clear_messages(message: types.Message):
    d = dialogs.get_dialog(message.from_user.id)
    if d is None:
        await message.reply(render_template('not_dialog.j2', {'user_id': message.from_user.id}))
    else:
        d.empty_messages()
        await message.reply(render_template('dialog_cleared.j2',{
            'user_id': message.from_user.id,
            'total_tokens': d.total_tokens_num()
        }))

@dp.message_handler(commands=['dialogs'])
async def dialogs_info(message: types.Message):
    info = dialogs.get_dialogs_info()
    await message.reply(render_template('dialogs_info.j2', {'info': info}))

async def error_answer_and_log(msg:types.Message , text: str):
    await msg.answer(text)
    logging.error(text)

@dp.message_handler()
async def echo(message: types.Message):
    d = dialogs.get_dialog(message.from_user.id)
    if d is None:
        d = dialogs.create_dialog(message.from_user.id)
    d.append_message('user', message.text)
    msg = await message.answer("🔎 Идет генерация, подождите...")
    messages_list = d.get_messages()
    try:
        completion: openai.ChatCompletion = openai.ChatCompletion.create(
            model=dialogs.model,
            messages=messages_list,
            stream = True
        )

        answer = ''
        role = ''
        begin_time = 0
        for chunk in completion:
            if 'role' in chunk['choices'][0]['delta']:
                role = chunk['choices'][0]['delta']['role']
            if 'content' in chunk['choices'][0]['delta']:
                answer = answer + chunk['choices'][0]['delta']['content']
                current_time = time.time()
                if current_time - begin_time > 2:
                    await msg.edit_text(answer)
                    begin_time = current_time

        await msg.edit_text(f'{answer} \n ---------------------')
        d.append_message(role, answer)
        regexp = '\.\d*$'
        logging.info(f"{re.sub(regexp, '', datetime.now().__str__())}-------------------------------------------------")
        logging.info(f"Диалог. Токены - {d.total_tokens_num()}, реплики: {len(d)}")
        logging.info(f"Запрос от {message.from_user['id']}: {message.text[:30]}...")
        corrected_answer = answer[:30].replace('\n', ' ')
        logging.info(f"Ответ: {corrected_answer}...")
    except APIError as e:
        err_msg = f"Произошла ошибка API Error: {e}. Попробуйте задать вопрос снова"
        await error_answer_and_log(message, err_msg)
    except Timeout as e:
        err_msg = f"Произошла ошибка Timeout Error: {e} Попробуйте задать вопрос снова"
        await error_answer_and_log(message, err_msg)
    except RateLimitError as e:
        err_msg=f"Произошла ошибка Rate Limit Error: {e} Попробуйте задавать вопросы пореже"
        await error_answer_and_log(message, err_msg)
    except APIConnectionError as e:
        err_msg=f"Произошла ошибка Connection Error: {e} Проверьте подключение к сети"
        await error_answer_and_log(message, err_msg)
    except InvalidRequestError as e:
        err_msg=f"Произошла ошибка Invalid Request Error: {e} Программист что-то накосячил. Сообщите об этом ему"
        await error_answer_and_log(message, err_msg)
    except AuthenticationError as e:
        err_msg=f"Произошла ошибка Authentication Error: {e} Программист накосячил с ключами. Сообщите об этом ему"
        await error_answer_and_log(message, err_msg)
    except ServiceUnavailableError as e:
        err_msg=f"Произошла ошибка Service Unavailable Error: {e} Сервис OpenAI недоступен. Надо подождать."
        await error_answer_and_log(message, err_msg)

@dp.message_handler(content_types=[ContentType.VOICE])
async def voice_handler(message:types.Message):
    voice = await message.voice.get_file()
    ogg_file = NamedTemporaryFile(delete=False, prefix='bot-ogg-')
    ogg_file.close()
    await bot.download_file(voice.file_path, ogg_file.name)
    ogg_voice = AudioSegment.from_ogg(ogg_file.name)
    os.remove(ogg_file.name)
    mp3_file = NamedTemporaryFile(delete=False, prefix='bot-mp3-', suffix='.mp3')
    mp3_file.close()
    ogg_voice.export(mp3_file.name, format='mp3')
    audio_for_gpt = open(mp3_file.name, 'rb')
    msg = await message.answer("🔎 Идет распознавание, подождите...")
    transcript = openai.Audio.transcribe("whisper-1", audio_for_gpt)
    os.remove(mp3_file.name)
    await msg.edit_text(transcript.text)







if __name__ == '__main__':
    print('bot started...')
    executor.start_polling(dp, skip_updates=True)
