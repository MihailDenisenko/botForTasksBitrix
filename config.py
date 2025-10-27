import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BITRIX_URL = os.getenv("BITRIX_URL")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не установлен в .env файле!")
if not BITRIX_URL:
    raise ValueError("❌ BITRIX_URL не установлен в .env файле!")

# Настройки Bitrix24
BITRIX_TIMEOUT = 10
MAX_TASKS_DISPLAY = 10