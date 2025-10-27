import requests
from config import BITRIX_URL, BITRIX_TIMEOUT

class BitrixClient:
    def __init__(self):
        self.base_url = BITRIX_URL
        self.timeout = BITRIX_TIMEOUT

    def _make_request(self, method, payload):
        """Базовый метод для запросов к Bitrix24"""
        url = f"{self.base_url}{method}"
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Ошибка запроса к Bitrix24 ({method}): {e}")
            return {"error": str(e)}

    def get_projects(self):
        """Получает проекты из Bitrix24"""
        payload = {
            "select": ["ID", "NAME"],
            "filter": {"PROJECT": "Y", "ACTIVE": "Y"}
        }
        result = self._make_request("sonet_group.get", payload)
        return {project["NAME"]: project["ID"] for project in result.get("result", [])}

    def get_users(self):
        """Получает пользователей из Bitrix24"""
        payload = {
            "select": ["ID", "NAME", "LAST_NAME", "EMAIL"],
            "filter": {"ACTIVE": True}
        }
        result = self._make_request("user.get", payload)
        return result.get("result", [])

    def create_task(self, title, description, responsible_id, group_id=None):
        """Создает задачу в Bitrix24"""
        task_data = {
            "fields": {
                "TITLE": title,
                "DESCRIPTION": description,
                "RESPONSIBLE_ID": responsible_id
            }
        }
        
        if group_id:
            task_data["fields"]["GROUP_ID"] = group_id
        
        result = self._make_request("tasks.task.add", task_data)
        
        if "result" in result:
            return {"success": True, "task_id": result["result"]["task"]["id"]}
        else:
            return {"success": False, "error": result.get("error_description", "Unknown error")}

    def get_tasks(self, limit=10, start=0):
        """Получает список задач из Bitrix24"""
        payload = {
            "select": ["ID", "TITLE", "DESCRIPTION", "STATUS", "RESPONSIBLE_ID", "CREATED_DATE", "DEADLINE", "PRIORITY", "GROUP_ID"],
            "order": {"ID": "DESC"},
            "filter": {},
            "start": start
        }
        
        result = self._make_request("tasks.task.list", payload)
        tasks = result.get("result", {}).get("tasks", [])
        return tasks[:limit] if limit else tasks

    def get_task_by_id(self, task_id):
        """Получает конкретную задачу по ID"""
        payload = {
            "taskId": task_id,
            "select": ["ID", "TITLE", "DESCRIPTION", "STATUS", "RESPONSIBLE_ID", "CREATED_DATE", "CREATED_BY", "DEADLINE", "PRIORITY", "GROUP_ID", "TIME_ESTIMATE"]
        }
        
        result = self._make_request("tasks.task.get", payload)
        return result.get("result", {}).get("task")

    def test_connection(self):
        """Проверяет подключение к Bitrix24"""
        try:
            response = requests.post(f"{self.base_url}profile", timeout=self.timeout)
            return response.status_code == 200
        except:
            return False

# Создаем глобальный экземпляр клиента
bitrix_client = BitrixClient()