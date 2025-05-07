import httpx

API_TOKEN = "pk_95539169_SZWH0M6K10ZAK6B73S5MW4SUHZDATTI7"
LIST_ID = "901802385048"
BASE_URL = f"https://api.clickup.com/api/v2/list/901802385048/task"

HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}


async def fetch_task_page(client: httpx.AsyncClient, page: int, start_ts: int, end_ts: int):
    params = {
        "page": page,
        "due_date_gt": start_ts,
        "due_date_lt": end_ts
    }
    response = await client.get(BASE_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()
