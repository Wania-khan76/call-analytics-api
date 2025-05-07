import httpx
from collections import defaultdict
from datetime import datetime, timedelta
from app.models.schemas import PendingTasksResponse
from app.external.pending_client import fetch_task_page


def get_date_range(start_date_str=None, end_date_str=None):
    today = datetime.today()
    start = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else today - timedelta(days=30)
    end = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else today
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


async def get_pending_tasks(start_date=None, end_date=None) -> PendingTasksResponse:
    start_ts, end_ts = get_date_range(start_date, end_date)
    async with httpx.AsyncClient(timeout=10) as client:
        pending_by_date = defaultdict(int)
        total_pending = 0
        page = 0

        while True:
            data = await fetch_task_page(client, page, start_ts, end_ts)
            tasks = data.get("tasks", [])
            if not tasks:
                break

            for task in tasks:
                if task.get("status", {}).get("status", "").lower() == "pending":
                    created_ts = int(task.get("date_created", 0))
                    date_str = datetime.fromtimestamp(created_ts / 1000).strftime("%Y-%m-%d")
                    pending_by_date[date_str] += 1
                    total_pending += 1
            page += 1

        return PendingTasksResponse(
            total_pending_calls=total_pending,
            date_wise=[
                {"date": date, "pending_calls": count}
                for date, count in sorted(pending_by_date.items())
            ]
        )
