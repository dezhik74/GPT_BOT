from decouple import config

TELEGA_TOKEN = config('TELEGA_TOKEN')

OPENAI_API_URL = 'https://free.churchless.tech/v1/chat/completions'

OPENAI_API_TOKEN = config('OPENAI_API_TOKEN')

MAX_SYBOLS_IN_CHAT = 7800

