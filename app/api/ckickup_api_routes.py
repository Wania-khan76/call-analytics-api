import asyncio
import aiohttp
from typing import Optional
from app.core.config import Settings
from fastapi import APIRouter, Query,HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from datetime import date
from collections import defaultdict
import logging
from app.core.config import settings  # Import settings if you want to use config
from app.models.schemas import PendingTasksResponse
from app.services.pending_service import get_pending_tasks
from app.services.payment_service import get_payment_report
from app.models.schemas import PaymentReportResponse
router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility function to format timestamps
def format_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')

async def fetch_with_retries(url, params, headers, retries=3, delay=1):
    async with aiohttp.ClientSession() as session:
        for i in range(retries):
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Attempt {i+1} failed with status {response.status}")
                        await asyncio.sleep(delay)
                        delay *= 2  # Exponential backoff
            except Exception as e:
                logger.warning(f"Attempt {i+1} failed with exception: {str(e)}")
                await asyncio.sleep(delay)
                delay *= 2
        raise Exception(f"Failed to fetch data after {retries} retries")

async def fetch_tasks_from_list(list_id, custom_field_id, headers, start_ts, end_ts, session):
    matched = []
    page = 0
    while True:
        params = {
            "include_closed": "true",
            "subtasks": "true",
            "page": page
        }

        try:
            tasks = await fetch_with_retries(
                f"https://api.clickup.com/api/v2/list/{list_id}/task",
                params,
                headers
            )
            if not tasks.get("tasks"):
                break

            for task in tasks["tasks"]:
                for field in task.get("custom_fields", []):
                    if field.get("id") == custom_field_id and field.get("value"):
                        try:
                            survey_date = int(field["value"])
                            if start_ts <= survey_date < end_ts:
                                matched.append(survey_date)
                        except Exception as e:
                            logger.error(f"Error processing field in task {task['id']}: {e}")

            if len(tasks["tasks"]) < 100:
                break
            page += 1
        except Exception as e:
            logger.error(f"Error fetching tasks for list {list_id}: {e}")
            break

    return matched

async def fetch_installed_tasks(list_id, date_field_id, hour_field_id, headers, start_ts, end_ts, session):
    total_count = 0
    total_hours = 0
    date_wise = defaultdict(lambda: {"count": 0, "daywise_hours": 0})
    page = 0

    while True:
        params = {
            "include_closed": "true",
            "subtasks": "true",
            "page": page
        }

        try:
            tasks = await fetch_with_retries(
                f"https://api.clickup.com/api/v2/list/{list_id}/task",
                params,
                headers
            )
            if not tasks.get("tasks"):
                break

            for task in tasks["tasks"]:
                survey_date = None
                install_hours = 0

                for field in task.get("custom_fields", []):
                    if field.get("id") == date_field_id and field.get("value"):
                        survey_date = int(field["value"])
                    elif field.get("id") == hour_field_id and field.get("value") is not None:
                        try:
                            install_hours = float(field["value"])
                        except ValueError:
                            install_hours = 0

                if survey_date and start_ts <= survey_date < end_ts and install_hours > 0:
                    total_count += 1
                    total_hours += install_hours
                    date_str = format_timestamp(survey_date)
                    date_wise[date_str]["count"] += 1
                    date_wise[date_str]["daywise_hours"] += install_hours

            if len(tasks["tasks"]) < 100:
                break
            page += 1
        except Exception as e:
            logger.error(f"Error fetching tasks for list {list_id}: {e}")
            break

    return {
        "total_installed_surveys": total_count,
        "total_installed_hours": total_hours,
        "date_wise_count": [
            {"date": d, "count": v["count"], "daywise_hours": v["daywise_hours"]}
            for d, v in sorted(date_wise.items())
        ]
    }

@router.get("/total-survey")
async def total_survey(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    try:
        input_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = input_date - timedelta(days=30)
        end_date = input_date + timedelta(days=1)
        start_ts = int(start_date.timestamp() * 1000)
        end_ts = int(end_date.timestamp() * 1000)

        # Consider moving this to your config file
        clickup_token = "pk_95539169_SZWH0M6K10ZAK6B73S5MW4SUHZDATTI7"
        custom_field_id = "4f8bf712-7ef4-457a-93f9-ad0598b1fefc"
        headers = {"Authorization": clickup_token}

        list_info = [
            {"id": "901802111908", "name": "📦 Installation"},
            {"id": "901802098213", "name": "✅ Installed"},
            {"id": "901802083406", "name": "🔄 Follow-up"},
        ]

        async with aiohttp.ClientSession() as session:
            all_survey_dates = await asyncio.gather(
                *[fetch_tasks_from_list(lst["id"], custom_field_id, headers, start_ts, end_ts, session) for lst in list_info]
            )

        all_survey_dates = [date for sublist in all_survey_dates for date in sublist]

        date_count = defaultdict(int)
        for ts in all_survey_dates:
            date_str = format_timestamp(ts)
            date_count[date_str] += 1

        result = {
            "total_survey_count": len(all_survey_dates),
            "date_wise_count": [{"date": d, "count": c} for d, c in sorted(date_count.items())]
        }

        return JSONResponse(content=result)

    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid date format. Use YYYY-MM-DD."})
    except Exception as e:
        logger.error(f"Unexpected error in total_survey: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

@router.get("/installed-survey")
async def installed_survey(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    try:
        input_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = input_date - timedelta(days=30)
        end_date = input_date + timedelta(days=1)
        start_ts = int(start_date.timestamp() * 1000)
        end_ts = int(end_date.timestamp() * 1000)

        # Consider moving this to your config file
        clickup_token = "pk_95539169_SZWH0M6K10ZAK6B73S5MW4SUHZDATTI7"
        headers = {"Authorization": clickup_token}

        list_id = "901802098213"  # ✅ Installed
        date_field_id = "4f8bf712-7ef4-457a-93f9-ad0598b1fefc"
        hour_field_id = "0336d5ec-41c1-4785-89b8-0b63bfaa9150"

        async with aiohttp.ClientSession() as session:
            installed_data = await fetch_installed_tasks(
                list_id, date_field_id, hour_field_id, headers, start_ts, end_ts, session
            )

        return JSONResponse(content=installed_data)

    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid date format. Use YYYY-MM-DD."})
    except Exception as e:
        logger.error(f"Unexpected error in installed_survey: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
    

@router.get("/pending-tasks", response_model=PendingTasksResponse)
async def pending_tasks(
    start_date: str = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(default=None, description="End date (YYYY-MM-DD)")
):
    return await get_pending_tasks(start_date, end_date)



@router.get("/payments-report", response_model=PaymentReportResponse)
async def payments_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
  

    try:
        return await get_payment_report(start_date, end_date)  # Directly return the response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))