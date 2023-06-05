from pathlib import Path

from decouple import config

TELEGA_TOKEN = config('TELEGA_TOKEN')

OPENAI_API_TOKEN = config('OPENAI_API_TOKEN')

MAX_SYBOLS_IN_CHAT = 7800

MAX_TOKENS_IN_DIALOG = 4096

admin_ids = [539952792]

IN_DOCKER = config('IN_DOCKER', cast=bool)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"


