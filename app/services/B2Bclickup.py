import requests
from typing import List, Dict
from app.core.config import settings
from app.models.schemas import ClickUpTask
from fastapi import HTTPException

class ClickUpService:
    def __init__(self):
        self.api_key = settings.clickup_api_key
        self.base_url = "https://api.clickup.com/api/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        })

    def get_tasks_by_tag(self, list_ids: List[str], tag_name: str) -> List[ClickUpTask]:
        all_tasks = []
        for list_id in list_ids:
            try:
                page = 0
                while True:
                    params = {
                        "include_closed": "true",
                        "subtasks": "true",
                        "tags[]": tag_name,
                        "page": page
                    }
                    url = f"{self.base_url}/list/{list_id}/task"
                    response = self.session.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    tasks = data.get("tasks", [])
                    if not tasks:
                        break
                    all_tasks.extend([ClickUpTask(**task) for task in tasks])
                    page += 1
            except requests.exceptions.RequestException as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"ClickUp API error for list {list_id}: {str(e)}"
                )
        return all_tasks