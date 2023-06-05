from gpt_bot.tokens_num import num_tokens_from_message


def test_tokens_num():
    message = '''
        Hello there! It's great to hear that you're enjoying GPT. How can I assist you today?
    '''
    tn = num_tokens_from_message(message)
    assert tn == 32

