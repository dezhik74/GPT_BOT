from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from gpt_bot.config import admin_ids


def get_main_kb (telega_id: int):
    b1 = KeyboardButton('/start')
    b2 = KeyboardButton('/status')
    b3 = KeyboardButton('/clear')
    b4 = KeyboardButton('расскажи анекдот')

    kb_main = ReplyKeyboardMarkup(resize_keyboard=True)

    if telega_id in admin_ids:
        kb_main.row(b1, b2, b3, b4)
    else:
        kb_main.row(b1, b2)

    return kb_main


