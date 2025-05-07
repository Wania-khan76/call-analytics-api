import requests
import json
import datetime
from fastapi import HTTPException
from typing import List, Dict, Optional
import logging

# Config
CLICKUP_API_KEY = 'your_clickup_api_key_here'
LIST_ID = '901802098213'

FIELD_FEEDBACK_DATE = "d2b081ca-7d1d-4cd8-b566-c0253e0bc3ef"
FIELD_FEEDBACK_STATUS = "94af4590-8615-4e69-87fb-336bc8782cd1"
FIELD_FEEDBACK_COMMENTS = "88b1a2ec-6dd5-4122-b4b5-bef49959306e"
FIELD_FEEDBACK_NPS = "6ce23687-8774-42c5-96fb-6b56ef3aea74"
STATUS_DONE_ID = "ce0f8b64-71eb-483a-a858-c5f89ba3df88"

HEADERS = {
    'Authorization': "pk_95539169_SZWH0M6K10ZAK6B73S5MW4SUHZDATTI7",
    'Content-Type': 'application/json'
}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_unix_timestamp(date_str: str) -> int:
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)

def extract_custom_field(task: Dict, field_id: str) -> Optional[str]:
    for field in task.get("custom_fields", []):
        if field["id"] == field_id:
            value = field.get("value")
            if value is not None:
                return value.get("value") if isinstance(value, dict) else value
    return None

async def fetch_feedback_tasks(start_date: str, end_date: str) -> List[Dict]:
    logger.info(f"Fetching tasks from ClickUp for date range: {start_date} to {end_date}")
    start_ts = get_unix_timestamp(start_date)
    end_ts = get_unix_timestamp(end_date) + 86400000

    all_tasks = []
    page = 0
    max_pages = 10

    while page < max_pages:
        params = {
            'page': page,
            'limit': 100,
            'include_closed': 'true',
            'subtasks': 'true',
            'custom_fields': json.dumps([
                {"field_id": FIELD_FEEDBACK_STATUS, "operator": "=", "value": STATUS_DONE_ID},
                {"field_id": FIELD_FEEDBACK_DATE, "operator": ">=", "value": start_ts - 86400000},
                {"field_id": FIELD_FEEDBACK_DATE, "operator": "<=", "value": end_ts + 86400000}
            ])
        }

        try:
            response = requests.get(
                f"https://api.clickup.com/api/v2/list/{LIST_ID}/task",
                headers=HEADERS,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            tasks = data.get('tasks', [])
            if not tasks:
                logger.info("No tasks found for the given date range.")
                break

            logger.info(f"Found {len(tasks)} tasks on page {page + 1}")

            for task in tasks:
                feedback_ts = extract_custom_field(task, FIELD_FEEDBACK_DATE)
                if feedback_ts and start_ts <= int(feedback_ts) <= end_ts:
                    all_tasks.append(task)

            if len(tasks) < 100:
                logger.info("No more tasks to fetch. Exiting.")
                break

            page += 1
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")

    logger.info(f"Fetched {len(all_tasks)} tasks in total.")
    return all_tasks

