from os import environ
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

IS_THIS_LOCAL = "Pycharm" in str(Path.cwd())

TORTOISE_CONFIG = {
    "connections": {
        "telegram": environ['TG_PG_URL'],
        "bank": environ['BANK_PG_URL']
    },
    "apps": {
        "telegram": {"models": ["db_models.telegram"], "default_connection": "telegram"},
        "bank": {"models": ["db_models.bank"], "default_connection": "bank"}
    }
}

SECRET_KEY = environ['SECRET_KEY']

PROXY6NET_PROXIES = {"socks5://": environ['PROXY_HTTPS_URL']}
