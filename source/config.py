from os import environ
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

IS_THIS_LOCAL = "Pycharm" in str(Path.cwd())

TORTOISE_CONFIG = {
    "connections": {
        "bank": environ['BANK_PG_URL'],
        "declaration": environ['DC_PG_URL'],
        "telegram": environ['TG_PG_URL'],
    },
    "apps": {
        "bank": {"models": ["db_models.bank"], "default_connection": "bank"},
        "declaration": {"models": ["db_models.declaration"], "default_connection": "declaration"},
        "telegram": {"models": ["db_models.telegram"], "default_connection": "telegram"},
    }
}

SECRET_KEY = environ['SECRET_KEY']

PROXY6NET_PROXIES = {"socks5://": environ['PROXY_HTTPS_URL']}

JWT_SECRET = environ['JWT_SECRET']

APP_NAME = "task_sheduler"
