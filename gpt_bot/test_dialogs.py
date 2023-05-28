import pprint

import pytest

from gpt_bot.dialogs import Dialogs
from gpt_bot.tokens_num import num_tokens_from_message


def test_tokens_num():
    message = '''
        Hello there! It's great to hear that you're enjoying GPT. How can I assist you today?
    '''
    tn = num_tokens_from_message(message)
    assert tn == 32


def test_dialogs_create():
    ds = Dialogs()
    assert len(ds) == 0
    assert ds.model == 'gpt-3.5-turbo-0301'

@pytest.fixture(scope='module')
def dialogs():
    ds = Dialogs()
    ds.append_message_to_dialog('user', 'Hello world awesome GPT!', 1)
    ds.append_message_to_dialog('assistant', '''
        Hello there! It's great to hear that you're enjoying GPT. How can I assist you today?
    ''', 1)
    ds.append_message_to_dialog('user', 'Hello world awesome GPT!', 123)
    return ds

def test_dialog_append(dialogs):
    assert len(dialogs) == 2
    d1 = dialogs.get_dialog(1)
    assert d1 is not None
    assert d1.total_tokens_num() == 13 + 32
    assert d1.messages[0].tokens_num == 13
    assert d1.messages[1].tokens_num == 32
    assert len(d1) == 2
    d2 = dialogs.get_dialog(123)
    assert d2 is not None
    assert d2.total_tokens_num() == 13
    assert d2.messages[0].tokens_num == 13
    assert d2.messages[0].role == 'user'
    assert len(d2) == 1
    d3 = dialogs.get_dialog(34)
    assert d3 is None

def test_append_more_than_max(dialogs):
    # тест вставки в диалог, если превышен макс. размер по токенам
    # первый диалог - добавляем с max_tokens = 45, должен удалиться нулевой message
    dialogs.append_message_to_dialog('user', 'something else', 1, max_tokens=45)
    d1 = dialogs.get_dialog(1)
    assert len(d1) == 2
    s = '1'*105 #s - 42 токена
    # после этой вставки должен остаться один элемент
    # и это будет тот самый вставленный элемент
    dialogs.append_message_to_dialog('user', s, 1, max_tokens=45)
    assert len(d1) == 1
    assert d1.total_tokens_num() == 42
    assert d1.messages[0].role == 'user'

def test_empty_messages(dialogs):
    #тест полной очистки диалога
    d1 = dialogs.get_dialog(1)
    d1.empty_messages()
    assert len(d1) == 0
    assert d1.total_tokens_num() == 0


