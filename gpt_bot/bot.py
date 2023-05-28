import pprint
import time
from dataclasses import dataclass, field, asdict
from typing import List

from aiogram import Bot, Dispatcher, executor, types

from gpt_bot.dialogs import Dialogs
from main_keyboard import get_main_kb

import logging

import openai
from openai import APIError
from openai.error import RateLimitError, APIConnectionError, InvalidRequestError, AuthenticationError, \
    ServiceUnavailableError, Timeout

import config as config


# Configure logging
# logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a')
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.TELEGA_TOKEN)
dp = Dispatcher(bot)
openai.api_key = config.OPENAI_API_TOKEN
dialogs = Dialogs()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hello! I am bot for chatgpt 3.5. \nI am using paid subscription", reply_markup=get_main_kb(message.from_user.id))

@dp.message_handler(commands=['st', 'status'])
async def send_status(message: types.Message):
    print('---------------------------')
    await message.reply(f"""
        Статус выведен в консоль.
        Id пользователя: {message.from_user.id} 
        Диалог состоит из {dialogs.get_dialog_tokens_num(message.from_user.id)} токенов 
        Диалог состоит из {len(dialogs.dialogs[message.from_user.id])}
    """)

@dp.message_handler(commands=['clear'])
async def clear_messages(message: types.Message):
    dialogs.clear_dialog(message.from_user.id)
    await message.reply(f"""
        Диалог очищен.
        Id пользователя: {message.from_user.id} 
        Диалог состоит из {dialogs.get_dialog_tokens_num(message.from_user.id)} токенов\n
    """)

async def error_answer_and_log(msg:types.Message , text: str):
    await msg.answer(text)
    logging.error(text)



@dp.message_handler()
async def echo(message: types.Message):
    dialogs.append_message('user', message.text, message.from_user.id)
    msg = await message.answer(f"""🔎 Идет генерация, подождите...\n
        """, parse_mode="HTML")
    messages_list = dialogs.get_gpt_messages_for_dialog(message.from_user.id)
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
        dialogs.append_message(role, answer, message.from_user.id)

        logging.info("--------------------------------------------------------------------")
        logging.info(f"Диалог. Токены - {dialogs.get_dialog_tokens_num(message.from_user.id)}, реплики: {len(dialogs.dialogs[message.from_user.id])}")
        logging.info(f"Запрос от {message.from_user['id']}: {message.text[:30]}...")
        logging.info(f"Ответ: {answer[:30]}...")
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


if __name__ == '__main__':
    print('bot started...')
    executor.start_polling(dp, skip_updates=True)
