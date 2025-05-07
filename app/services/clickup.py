import requests
from fastapi import HTTPException
from datetime import datetime
from app.core.config import settings
import re

async def fetch_installed_leads(start_date: datetime, end_date: datetime):
    """Fetch installed leads from ClickUp API with proper phone extraction"""
    headers = {
        "Authorization": settings.CLICKUP_API_KEY,
        "Content-Type": "application/json"
    }
    
    url = f"https://api.clickup.com/api/v2/list/{settings.CLICK_UP_INSTALLED_LIST_ID}/task"
    
    start_timestamp = int(start_date.timestamp() * 1000)
    end_timestamp = int(end_date.timestamp() * 1000)
    
    all_tasks = []
    page = 0
    
    while True:
        params = {
            "page": page,
            "date_created_gt": start_timestamp,
            "date_created_lt": end_timestamp,
            "include_closed": "true"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"ClickUp list not found - verify list ID {settings.CLICK_UP_INSTALLED_LIST_ID}"
                )
                
            response.raise_for_status()
            data = response.json()
            
            if not data.get('tasks'):
                break
                
            # Process tasks to include URLs and raw phone data
            processed_tasks = []
            for task in data['tasks']:
                task['url'] = f"https://app.clickup.com/t/{task['id']}"
                processed_tasks.append(task)
                
            all_tasks.extend(processed_tasks)
            page += 1
            
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"ClickUp API Error: {str(e)}"
            )
    
    return all_tasks