import pprint
from dataclasses import dataclass, field, asdict
from typing import List

import openai

from aiogram import Bot, Dispatcher, executor, types


import logging

from openai import APIError
from openai.error import RateLimitError, APIConnectionError, InvalidRequestError, AuthenticationError, \
    ServiceUnavailableError, Timeout

import gpt_bot.config as config

# Configure logging
logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a')
# logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.TELEGA_TOKEN)
dp = Dispatcher(bot)
openai.api_key = config.OPENAI_API_TOKEN


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Привет! Я бот chatgpt 3.5. \nИспользую оплаченную подписку")

@dp.message_handler(commands=['st', 'status'])
async def send_status(message: types.Message):
    """
    Обработка команды st
    """
    print('---------------------------')
    pprint.pp(asdict(data))
    await message.reply(f"Статус выведен в консоль.\n Диалог состоит из {count_symbols(data)} символов ")

# @dp.message_handler()
# async def echo(message: types.Message):
#     res = ''
#     msg = await message.answer("🔎 Идет загрузка, подождите...")
    # print(message.text)
    # last_called = datetime.datetime.now()
    # throttle_sec = 0.5
    # for token in theb.Completion.create(message.text):
    #     res = res + token
    #     print(res)
    #     elapsed = datetime.datetime.now() - last_called
    #     remaining_time = throttle_sec - float(elapsed)
    #     print(f'last_called={last_called}; elaplsed={elapsed}; remaining_time={remaining_time}')
    #     if remaining_time > 0:
    #         last_called = datetime.datetime.now()
    #         await msg.edit_text(res)
    # await message.answer(res if res != '' else 'ответа не было')

    # await msg.edit_text(res)
        # print(token)
    # await msg.delete()
    # bot.delete_message(message.chat.id, msg.message_id)
    # await message.answer(res)

@dataclass
class GPTMessage:
    role: str
    content: str

@dataclass
class ChatData:
    model: str = 'gpt-3.5-turbo'
    messages: List[GPTMessage] = field(default_factory=list)

data = ChatData()

def count_symbols(d: ChatData) -> int:
    res = 0
    for m in d.messages:
        res = res + len(m.content)
    return res

def clear_messages(arr : List[GPTMessage], n) -> List[GPTMessage]:
    total_key2_length = sum(len(d.content) for d in arr)
    i = 0
    while total_key2_length >= n and i < len(arr):
        total_key2_length -= len(arr[i].content)
        i += 1
    return arr[i:]

async def error_answer_and_log(msg:types.Message , text: str):
    await msg.answer(text)
    logging.error(text)


print(data)

@dp.message_handler()
async def echo(message: types.Message):
    data.messages.append(GPTMessage(role='user', content=message.text))
    data.messages = clear_messages(data.messages, config.MAX_SYBOLS_IN_CHAT)
    await message.answer(f"""🔎 Идет генерация, подождите...\n
        <i>Диалог состоит из {count_symbols(data)} символов\n
        В диалоге {len(data.messages)} реплик</i>\n
        """, parse_mode="HTML")
    messages_list = [asdict(m) for m in data.messages]
    try:
        completion: openai.ChatCompletion = openai.ChatCompletion.create(
            model=data.model,
            messages=messages_list
        )
        data.messages.append(
            GPTMessage(role=completion.choices[0].message['role'],
                       content=completion.choices[0].message['content'])
        )

        await message.answer(f"""
            {completion.choices[0].message['content']} \n\n 
            Использование токенов {completion['usage']['total_tokens']}
        """)
        logging.info("--------------------------------------------------------------------")
        logging.info(f"Диалог. Символы - {count_symbols(data)}, реплики: {len(data.messages)}")
        logging.info(f"Использовано токенов: {completion['usage']['total_tokens']}")
        logging.info(f"Запрос от {message.from_user['id']}: {message.text[:30]}...")
        logging.info(f"Ответ: {completion.choices[0].message['content'][:30]}...")
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




# @dp.message_handler()
# Это через халявный API
# async def echo(message: types.Message):
#     data.messages.append(GPTMessage(role='user', content=message.text))
#     headers = {'Content-Type': 'application/json'}
#     msg = await message.answer(f"🔎 Идет генерация, подождите... \nДиалог состоит из {count_symbols(data)} символов")
#     print(f'data={asdict(data)}')
#     async with aiohttp.ClientSession() as session:
#         async with session.post(config.OPENAI_API_URL, headers=headers, json=asdict(data)) as resp:
#             print(resp.status)
#             json = await resp.json()
#             # print(json['choices'][0]['message']['content'])
#             pprint.pp(json)
#             data.messages.append(
#                 GPTMessage(role=json['choices'][0]['message']['role'],
#                            content=json['choices'][0]['message']['content']))
#             await message.answer(json["choices"][0]["message"]["content"])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
