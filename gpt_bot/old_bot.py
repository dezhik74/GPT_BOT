import pprint
import time
from dataclasses import dataclass, field, asdict
from typing import List

from aiogram import Bot, Dispatcher, executor, types
from main_keyboard import get_main_kb

import logging

import openai
from openai import APIError
from openai.error import RateLimitError, APIConnectionError, InvalidRequestError, AuthenticationError, \
    ServiceUnavailableError, Timeout

import config as config


# Configure logging
logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a')
# logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.TELEGA_TOKEN)
dp = Dispatcher(bot)
openai.api_key = config.OPENAI_API_TOKEN


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот chatgpt 3.5. \nИспользую оплаченную подписку", reply_markup=get_main_kb(message.from_user.id))

@dp.message_handler(commands=['st', 'status'])
async def send_status(message: types.Message):
    print('---------------------------')
    pprint.pp(asdict(data))
    await message.reply(f"Статус выведен в консоль.\n Диалог состоит из {count_symbols_in_dialog(data)} символов ")

@dp.message_handler(commands=['clear'])
async def clear_messages(message: types.Message):
    data.messages = []
    await message.reply(f"Диалог очищен.\n Диалог состоит из {count_symbols_in_dialog(data)} символов ")


@dataclass
class GPTMessage:
    role: str
    content: str

@dataclass
class ChatData:
    model: str = 'gpt-3.5-turbo'
    messages: List[GPTMessage] = field(default_factory=list)

data = ChatData()

def count_symbols_in_dialog(d: ChatData) -> int:
    res = 0
    for m in d.messages:
        res = res + len(m.content)
    return res

def correct_messages_number(arr : List[GPTMessage], n) -> List[GPTMessage]:
    total_key2_length = sum(len(d.content) for d in arr)
    i = 0
    while total_key2_length >= n and i < len(arr):
        total_key2_length -= len(arr[i].content)
        i += 1
    return arr[i:]

async def error_answer_and_log(msg:types.Message , text: str):
    await msg.answer(text)
    logging.error(text)



@dp.message_handler()
async def echo(message: types.Message):
    data.messages.append(GPTMessage(role='user', content=message.text))
    data.messages = correct_messages_number(data.messages, config.MAX_SYBOLS_IN_CHAT)
    msg = await message.answer(f"""🔎 Идет генерация, подождите...\n
        <i>Диалог состоит из {count_symbols_in_dialog(data)} символов\n
        В диалоге {len(data.messages)} реплик</i>\n
        """, parse_mode="HTML")
    messages_list = [asdict(m) for m in data.messages]
    try:
        completion: openai.ChatCompletion = openai.ChatCompletion.create(
            model=data.model,
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
        data.messages.append(
            GPTMessage(role=role, content=answer)
        )

        logging.info("--------------------------------------------------------------------")
        logging.info(f"Диалог. Символы - {count_symbols_in_dialog(data)}, реплики: {len(data.messages)}")
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
