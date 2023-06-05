import pytest

from gpt_bot.templates import render_template


def test_status_not_dialog():
    m = render_template('not_dialog.j2', {'user_id': 555})
    assert m == """Вы еще на начали диалог.\nId пользователя: 555"""