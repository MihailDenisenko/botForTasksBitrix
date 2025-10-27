import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher

# Добавляем текущую директорию в путь Python для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BOT_TOKEN
from utils.helpers import set_bot_commands
from services.bitrix_client import bitrix_client

# Импортируем роутеры
from handlers.commands import router as commands_router
from handlers.task_creation import router as task_creation_router
from handlers.quick_tasks import router as quick_tasks_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск бота...")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрируем роутеры
    dp.include_router(commands_router)
    dp.include_router(task_creation_router)
    dp.include_router(quick_tasks_router)
    
    # Устанавливаем меню команд
    await set_bot_commands(bot)
    logger.info("✅ Меню команд настроено")
    
    # Проверяем подключение к Bitrix24
    if bitrix_client.test_connection():
        logger.info("✅ Подключение к Bitrix24 установлено")
    else:
        logger.warning("⚠️ Внимание: проблемы с подключением к Bitrix24")
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())