import pytest

from gpt_bot.utils import pre_tag


def test_pre_tag():
    s = "'''python строка для превращения''' просто текст "
    print('-----')
    print(s)
    print(pre_tag(s))
    print('-----')
