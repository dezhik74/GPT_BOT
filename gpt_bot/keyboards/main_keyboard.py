from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('/start')
b2 = KeyboardButton('/status')
b3 = KeyboardButton('/clear')

kb_main = ReplyKeyboardMarkup(resize_keyboard=True)

kb_main.row(b1, b2, b3)