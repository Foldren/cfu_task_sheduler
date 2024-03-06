from os import environ
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

IS_THIS_LOCAL = "Pycharm" in str(Path.cwd())

POSTGRES_URL = environ['PG_URL']

SECRET_KEY = environ['SECRET_KEY']

PROXY6NET_PROXIES = {"socks5://": environ['PROXY_HTTPS_URL']}
