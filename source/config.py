from os import getenv
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URL = getenv("POSTGRES_URL")
SECRET_KEY = getenv('SECRET_KEY')
PROXY6NET_PROXIES = {"socks5://": getenv('PROXY_HTTPS_URL')}
