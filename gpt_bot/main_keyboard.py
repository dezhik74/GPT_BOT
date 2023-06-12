from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from gpt_bot import settings


def get_main_kb (telega_id: int):
    b1 = KeyboardButton('/start')
    b2 = KeyboardButton('/status')
    b3 = KeyboardButton('/clear')
    b4 = KeyboardButton('расскажи анекдот')
    b4a = KeyboardButton('tell a joke')
    b5 = KeyboardButton('/dialogs')

    kb_main = ReplyKeyboardMarkup(resize_keyboard=True)

    kb_main.row(b1, b2, b3)
    if telega_id in settings.admin_ids:
        kb_main.add(b4, b4a, b5)

    return kb_main


