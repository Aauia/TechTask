
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BITRIX_WEBHOOK = os.getenv("BITRIX_WEBHOOK")
