import re
from aiogram import Router, F
from aiogram.types import Message

from services.bitrix_client import bitrix_client

router = Router()

@router.message(F.text & (
    F.text.contains("задача") | 
    F.text.contains("постановка задачи") | 
    F.text.contains("поставить задачу")
))
async def quick_task_creation(message: Message):
    """Обрабатывает быстрое создание задачи через текстовый формат"""
    text = message.text.lower().strip()
    
    if any(cmd in text for cmd in ["/task", "/start", "/help"]):
        return
    
    pattern = r'#1\s*(.*?)(?=\s*#2|$)|#2\s*(.*?)(?=\s*#3|$)|#3\s*(\d+)(?=\s*#4|$)|#4\s*(\d+)?'
    matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
    
    if not matches:
        alt_pattern = r'#1\s*([^#]+?)\s+#2\s*([^#]+?)\s+#3\s*(\d+)(?:\s+#4\s*(\d+))?'
        alt_match = re.search(alt_pattern, text, re.IGNORECASE | re.DOTALL)
        if alt_match:
            title = alt_match.group(1).strip()
            description = alt_match.group(2).strip()
            responsible_id = int(alt_match.group(3))
            project_id = int(alt_match.group(4)) if alt_match.group(4) else 0
        else:
            await message.answer(
                "❌ <b>Неверный формат быстрого создания задачи!</b>\n\n"
                "📝 <b>Правильный формат:</b>\n"
                "<code>задача\n"
                "#1 Название задачи\n"
                "#2 Описание задачи\n" 
                "#3 ID исполнителя\n"
                "#4 ID проекта (не обязательно)</code>\n\n"
                "Или в одну строку:\n"
                "<code>поставить задачу #1 Название #2 Описание #3 123 #4 456</code>",
                parse_mode="HTML"
            )
            return
    else:
        title = ""
        description = ""
        responsible_id = None
        project_id = 0
        
        for match in matches:
            if match[0]:
                title = match[0].strip()
            elif match[1]:
                description = match[1].strip()
            elif match[2]:
                responsible_id = int(match[2])
            elif match[3]:
                project_id = int(match[3])
    
    if not title or not description or responsible_id is None:
        await message.answer(
            "❌ <b>Не хватает данных!</b>\n\n"
            "Обязательные поля:\n"
            "• #1 Название задачи\n" 
            "• #2 Описание задачи\n"
            "• #3 ID исполнителя\n\n"
            "Поле #4 ID проекта - не обязательное",
            parse_mode="HTML"
        )
        return
    
    group_id = project_id if project_id != 0 else None
    result = bitrix_client.create_task(title, description, responsible_id, group_id)
    
    if result["success"]:
        response = "✅ <b>Задача успешно создана!</b>"
        response += f"\n📋 <b>Название:</b> {title}"
        response += f"\n👤 <b>Исполнитель:</b> {responsible_id}"
        if group_id:
            response += f"\n🏗️ <b>Проект:</b> {group_id}"
        if "task_id" in result:
            response += f"\n🆔 <b>ID задачи в Bitrix:</b> {result['task_id']}"
    else:
        response = f"❌ <b>Ошибка создания задачи:</b>\n{result['error']}"
    
    await message.answer(response, parse_mode="HTML")