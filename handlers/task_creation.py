from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from models.states import TaskCreation
from services.bitrix_client import bitrix_client

router = Router()

@router.message(Command("task"))
async def cmd_task_dialog(message: Message, state: FSMContext):
    """Начинает диалог создания задачи"""
    await message.answer(
        "🎯 Начинаем создание задачи. Введите <b>название задачи</b>:",
        parse_mode="HTML"
    )
    await state.set_state(TaskCreation.waiting_title)

@router.message(TaskCreation.waiting_title)
async def process_title(message: Message, state: FSMContext):
    """Обрабатывает название задачи"""
    await state.update_data(title=message.text)
    await message.answer("📝 Теперь введите <b>описание задачи</b>:", parse_mode="HTML")
    await state.set_state(TaskCreation.waiting_description)

@router.message(TaskCreation.waiting_description)
async def process_description(message: Message, state: FSMContext):
    """Обрабатывает описание задачи"""
    await state.update_data(description=message.text)
    
    users = bitrix_client.get_users()
    if users:
        users_text = "\n".join([
            f"ID: {u['ID']} - {u['NAME']} {u.get('LAST_NAME', '')}"
            for u in users[:5]
        ])
        await message.answer(
            f"👥 <b>Доступные пользователи (первые 5):</b>\n{users_text}\n\n"
            "Введите <b>ID исполнителя</b>:",
            parse_mode="HTML"
        )
    else:
        await message.answer("Введите <b>ID исполнителя</b>:", parse_mode="HTML")
    
    await state.set_state(TaskCreation.waiting_responsible)

@router.message(TaskCreation.waiting_responsible)
async def process_responsible(message: Message, state: FSMContext):
    """Обрабатывает ID исполнителя"""
    try:
        responsible_id = int(message.text)
        await state.update_data(responsible_id=responsible_id)
        
        projects = bitrix_client.get_projects()
        if projects:
            projects_text = "\n".join([
                f"ID: {pid} - {name}" for name, pid in list(projects.items())[:5]
            ])
            await message.answer(
                f"🏗️ <b>Доступные проекты (первые 5):</b>\n{projects_text}\n\n"
                "Введите <b>ID проекта</b> (или 0 если без проекта):",
                parse_mode="HTML"
            )
        else:
            await message.answer("Введите <b>ID проекта</b> (или 0 если без проекта):", parse_mode="HTML")
        
        await state.set_state(TaskCreation.waiting_project)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Введите корректный ID:")

@router.message(TaskCreation.waiting_project)
async def process_project(message: Message, state: FSMContext):
    """Обрабатывает ID проекта и создает задачу"""
    try:
        project_id = int(message.text)
        data = await state.get_data()
        
        group_id = project_id if project_id != 0 else None
        
        result = bitrix_client.create_task(
            title=data["title"],
            description=data["description"],
            responsible_id=data["responsible_id"],
            group_id=group_id
        )
        
        if result["success"]:
            response = "✅ <b>Задача успешно создана!</b>"
            if group_id:
                response += f"\n🏗️ Проект: {group_id}"
            response += f"\n👤 Исполнитель: {data['responsible_id']}"
            if "task_id" in result:
                response += f"\n📋 ID задачи: {result['task_id']}"
        else:
            response = f"❌ <b>Ошибка создания задачи:</b>\n{result['error']}"
        
        await message.answer(response, parse_mode="HTML")
        await state.clear()
        
    except ValueError:
        await message.answer("❌ ID проекта должен быть числом. Введите корректный ID:")