import string


def english_letter_percentage(text):
    count = 0

    for char in text:
        if char in string.ascii_letters:
            count += 1

    return (count / len(text)) * 100 if len(text) > 0 else 0


def russian_letters_percent(input_str):
    russian_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    russian_letters += russian_letters.upper()  # Добавляем заглавные буквы
    russian_letters_count = 0
    for char in input_str:
        if char in russian_letters:
            russian_letters_count += 1
    percent = (russian_letters_count / len(input_str)) * 100
    return percent

def pre_tag(input_str):
    result_str = ''
    open_pre_count = 0
    i = 0
    while i < len(input_str):
        if input_str[i:i+3] == "```":
            open_pre_count += 1
            if open_pre_count % 2 != 0:
                result_str += '<pre>'
            else:
                result_str += '</pre>'
            i += 2
        else:
            result_str += input_str[i]
        i += 1
    if open_pre_count % 2 != 0:
        result_str += '</pre>'  # Добавляем закрывающий тег, если необходимо
    return result_str