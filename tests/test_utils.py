import pytest

from gpt_bot.utils import pre_tag


def test_pre_tag():
    s = "текст ```python строка для превращения```текст2 ```код 2```текст 3 ```без финальных кавычек"
    assert pre_tag(s) == "текст <pre>python строка для превращения</pre>текст2 <pre>код 2</pre>текст 3 <pre>без финальных кавычек</pre>"
