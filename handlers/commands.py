from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

from services.bitrix_client import bitrix_client
from services.task_formatter import task_formatter
from config import MAX_TASKS_DISPLAY

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда начала работы"""
    await message.answer(
        "🤖 Привет! Я бот для создания задач в Bitrix24\n\n"
        "📋 <b>Основные команды:</b>\n"
        "/task - Создать задачу через диалог\n"
        "/projects - Показать доступные проекты\n"
        "/users - Показать пользователей\n"
        "/gettasks - Получить список задач\n"
        "/help - Помощь\n\n"
        "💡 <b>Быстрое создание задачи:</b>\n"
        "Напиши <i>задача</i>, <i>постановка задачи</i> или <i>поставить задачу</i> "
        "и затем укажи данные в формате:\n"
        "<code>#1 Название задачи\n"
        "#2 Описание задачи\n"
        "#3 ID исполнителя\n"
        "#4 ID проекта (опционально)</code>",
        parse_mode="HTML"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Помощь по командам"""
    help_text = """
📖 <b>Помощь по использованию бота:</b>

<b>Создание задачи через диалог:</b>
/task - запускает пошаговое создание задачи

<b>Быстрое создание задачи:</b>
Напиши в чат:
<code>задача
#1 Название задачи
#2 Описание задачи  
#3 ID исполнителя
#4 ID проекта (не обязательно)</code>

<b>Просмотр задач:</b>
/gettasks - показать последние 10 задач
/gettasks 5 - показать 5 задач
/gettasks 1 - показать первую задачу подробно

<b>Другие команды:</b>
/projects - список проектов из Bitrix24
/users - список пользователей

💡 <b>Совет:</b> Используй меню внизу экрана для быстрого доступа к командам!
    """
    await message.answer(help_text, parse_mode="HTML")

@router.message(Command("projects"))
async def cmd_projects(message: Message):
    """Показывает проекты из Bitrix24"""
    await message.answer("🔄 Получаю список проектов из Bitrix24...")
    
    projects = bitrix_client.get_projects()
    if projects:
        projects_text = "\n".join([f"🏗️ <b>{name}</b> (ID: {pid})" for name, pid in projects.items()])
        response = f"📋 <b>Доступные проекты:</b>\n\n{projects_text}"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[])
        for name, pid in list(projects.items())[:8]:
            kb.inline_keyboard.append([
                InlineKeyboardButton(text=f"🏗️ {name[:20]}", callback_data=f"project_info:{pid}")
            ])
        
        await message.answer(response, parse_mode="HTML", reply_markup=kb)
    else:
        await message.answer("❌ Не удалось получить проекты или проекты не найдены")

@router.message(Command("users"))
async def cmd_users(message: Message):
    """Показывает пользователей"""
    await message.answer("🔄 Получаю список пользователей...")
    
    users = bitrix_client.get_users()
    if users:
        users_list = "\n".join([
            f"👤 <b>{user['NAME']} {user.get('LAST_NAME', '')}</b>\n"
            f"   ID: {user['ID']} | Email: {user.get('EMAIL', 'нет')}\n"
            for user in users[:10]
        ])
        response = f"👥 <b>Пользователи Bitrix24:</b>\n\n{users_list}"
        
        if len(users) > 10:
            response += f"\n... и еще {len(users) - 10} пользователей"
            
        await message.answer(response, parse_mode="HTML")
    else:
        await message.answer("❌ Не удалось получить список пользователей")

@router.message(Command("gettasks"))
async def cmd_get_tasks(message: Message):
    """Показывает список задач или конкретную задачу"""
    try:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if args and args[0].isdigit():
            task_count = int(args[0])
            
            if task_count == 1:
                tasks = bitrix_client.get_tasks(limit=1)
                if tasks:
                    task = tasks[0]
                    task_details = bitrix_client.get_task_by_id(task["id"])
                    response = task_formatter.format_task_info(task_details or task, detailed=True)
                else:
                    response = "❌ Задачи не найдены"
            else:
                tasks = bitrix_client.get_tasks(limit=task_count)
                if tasks:
                    response = f"📋 <b>Последние {len(tasks)} задач:</b>\n\n"
                    for i, task in enumerate(tasks, 1):
                        response += f"{i}. {task_formatter.format_task_info(task)}\n\n"
                else:
                    response = "❌ Задачи не найдены"
        else:
            tasks = bitrix_client.get_tasks(limit=MAX_TASKS_DISPLAY)
            if tasks:
                response = f"📋 <b>Последние {len(tasks)} задач:</b>\n\n"
                for i, task in enumerate(tasks, 1):
                    response += f"{i}. {task_formatter.format_task_info(task)}\n\n"
                
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="📖 Подробнее о первой задаче", callback_data="task_detail:first"),
                        InlineKeyboardButton(text="🔄 Обновить список", callback_data="refresh_tasks")
                    ]
                ])
                await message.answer(response, parse_mode="HTML", reply_markup=kb)
                return
            else:
                response = "❌ Задачи не найдены"
        
        await message.answer(response, parse_mode="HTML")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении задач: {e}")

@router.message()
async def handle_unknown_commands(message: Message):
    """Обрабатывает неизвестные команды"""
    if message.text.startswith('/'):
        await message.answer(
            "❌ Неизвестная команда. Используйте меню или одну из команд:\n\n"
            "📖 <b>Доступные команды:</b>\n"
            "/help - Помощь и инструкции\n"
            "/task - Создать задачу\n" 
            "/projects - Список проектов\n"
            "/users - Список пользователей\n"
            "/gettasks - Получить список задач",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "🤖 Я бот для работы с Bitrix24. Используйте меню команд или напишите:\n\n"
            "• /help - для помощи\n"
            "• /task - создать задачу\n"
            "• /gettasks - посмотреть задачи\n"
            "• <i>задача #1 Название #2 Описание #3 ID</i> - быстрый способ",
            parse_mode="HTML"
        )