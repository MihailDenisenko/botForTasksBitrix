from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_bot_commands(bot: Bot):
    """Устанавливает меню команд бота"""
    commands = [
        BotCommand(command="/help", description="📖 Помощь и инструкции"),
        BotCommand(command="/task", description="🎯 Создать задачу"),
        BotCommand(command="/projects", description="🏗️ Список проектов"),
        BotCommand(command="/users", description="👥 Список пользователей"),
        BotCommand(command="/gettasks", description="📋 Получить список задач"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())