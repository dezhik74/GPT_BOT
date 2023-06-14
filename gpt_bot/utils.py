import string


def english_letter_percentage(text):
    count = 0

    for char in text:
        if char in string.ascii_letters:
            count += 1

    return (count / len(text)) * 100 if len(text) > 0 else 0