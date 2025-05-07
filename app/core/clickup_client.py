
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class ClickUpClient:
    BASE_URL = "https://api.clickup.com/api/v2"
    
    def __init__(self):
        self.headers = {
            "Authorization": settings.CLICKUP_API_KEY,
            "Content-Type": "application/json"
        }
        self.list_ids = {
        "installation": settings.CLICK_UP_INTALLATION_LIST_ID,
        "installed": settings.CLICK_UP_INTALLED_LIST_ID,
        "follow_up": settings.CLICK_UP_FOLLOWUP_LIST_ID
    }
       
        self.survey_date_field_id = settings.SURVEY_DATE_FIELD_ID

    def get_survey_tasks_by_date_range(self, start_date: datetime) -> List[Dict[str, Any]]:
        """Get tasks filtered by survey date from start_date up to today"""
        all_tasks = []
        
        # Set end date to today at end of day
        end_date = datetime.now().replace(hour=23, minute=59, second=59)
        
        # Convert dates to Unix timestamps in milliseconds
        start_timestamp = int(start_date.timestamp() * 1000)
        end_timestamp = int(end_date.timestamp() * 1000)
        
        logger.info(f"Filtering tasks from {start_date} to {end_date}")
        logger.info(f"Using timestamps: {start_timestamp} to {end_timestamp}")
        
        for list_name, list_id in self.list_ids.items():

            try:
                tasks = self._get_filtered_tasks_from_list(
                    list_id=list_id,
                    start_timestamp=start_timestamp,
                    end_timestamp=end_timestamp
                )
                if tasks:
                    all_tasks.extend(tasks)
                    logger.info(f"Found {len(tasks)} tasks in list {list_id}")
            except Exception as e:
                logger.error(f"Error fetching tasks from list {list_id}: {e}")
        
        logger.info(f"Total tasks found in date range: {len(all_tasks)}")
        return all_tasks

    def _get_filtered_tasks_from_list(self, list_id: str, 
                                    start_timestamp: int,
                                    end_timestamp: int) -> List[Dict[str, Any]]:
        page = 0
        all_tasks = []
        
        while True:
            params = {
                'page': page,
                'limit': 100,
                'subtasks': 'true',
                'include_closed': 'true',
                'date_updated_gt': start_timestamp - (86400 * 1000),  # 1 day before
                'custom_fields': json.dumps([{
                    "field_id": self.survey_date_field_id,
                    "operator": ">=",
                    "value": start_timestamp
                }, {
                    "field_id": self.survey_date_field_id,
                    "operator": "<=",
                    "value": end_timestamp
                }])
            }
            
            try:
                response = requests.get(
                    f"{self.BASE_URL}/list/{list_id}/task",
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                tasks = data.get('tasks', [])
                
                if not tasks:
                    break
                    
                all_tasks.extend(tasks)
                
                # Stop if we've reached the API limit
                if len(all_tasks) >= 1000:  # Safety limit
                    break
                    
                page += 1
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                if hasattr(e, 'response') and e.response:
                    logger.error(f"Response: {e.response.text}")
                break
            
        return all_tasks