from datetime import datetime
from services.bitrix_client import bitrix_client

class TaskFormatter:
    def __init__(self):
        self.status_map = {
            "1": "🆕 Новая",
            "2": "⏳ Ожидает выполнения", 
            "3": "🚀 Выполняется",
            "4": "🔄 Ожидает контроля",
            "5": "✅ Завершена",
            "6": "❌ Отложена",
            "7": "🗑️ Удалена"
        }
        
        self.priority_map = {
            "0": "🟢 Низкий",
            "1": "🟡 Средний",
            "2": "🔴 Высокий"
        }

    def _get_user_name(self, user_id):
        """Получает имя пользователя по ID"""
        users = bitrix_client.get_users()
        for user in users:
            if str(user["ID"]) == str(user_id):
                return f"{user['NAME']} {user.get('LAST_NAME', '')}"
        return f"Пользователь {user_id}"

    def _get_project_name(self, project_id):
        """Получает название проекта по ID"""
        projects = bitrix_client.get_projects()
        for name, pid in projects.items():
            if str(pid) == str(project_id):
                return name
        return f"Проект {project_id}"

    def _format_date(self, date_str):
        """Форматирует дату"""
        if not date_str:
            return ""
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%d.%m.%Y %H:%M')
        except:
            return date_str

    def format_task_info(self, task, detailed=False):
        """Форматирует информацию о задаче для вывода"""
        if not task:
            return "❌ Задача не найдена"
        
        task_id = task.get("id", "N/A")
        title = task.get("title", "Без названия")
        description = task.get("description", "Без описания")
        status = self.status_map.get(str(task.get("status", "1")), "❓ Неизвестно")
        priority = self.priority_map.get(str(task.get("priority", "1")), "🟡 Средний")
        responsible_id = task.get("responsibleId", "")
        created_date = task.get("createdDate", "")
        deadline = task.get("deadline", "")
        group_id = task.get("groupId", "")
        
        responsible_name = self._get_user_name(responsible_id)
        
        if detailed:
            response = f"📋 <b>Задача #{task_id}</b>\n\n"
            response += f"<b>Название:</b> {title}\n"
            response += f"<b>Описание:</b> {description}\n"
            response += f"<b>Статус:</b> {status}\n"
            response += f"<b>Приоритет:</b> {priority}\n"
            response += f"<b>Исполнитель:</b> {responsible_name}\n"
            
            if created_date:
                response += f"<b>Создана:</b> {self._format_date(created_date)}\n"
            
            if deadline:
                response += f"<b>Дедлайн:</b> {self._format_date(deadline)}\n"
            
            if group_id:
                project_name = self._get_project_name(group_id)
                response += f"<b>Проект:</b> {project_name}\n"
        else:
            response = f"• <b>#{task_id}</b> {title} - {status}\n"
            response += f"  👤 {responsible_name}"
            
            if deadline:
                deadline_formatted = self._format_date(deadline)
                if deadline_formatted:
                    response += f" | 📅 {deadline_formatted.split()[0]}"
        
        return response

# Глобальный экземпляр форматтера
task_formatter = TaskFormatter()