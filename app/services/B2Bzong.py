import requests
import datetime
from typing import List, Dict, Optional
from app.core.config import settings
from app.models.schemas import ZongCallRecord
from fastapi import HTTPException

class ZongService:
    def __init__(self):
        self.base_url = settings.zong_base_url
        self.token = settings.zong_token
        self.vpbx_id = settings.zong_vpbx_id
        self.session = requests.Session()
        self.session.verify = False

    def get_call_records(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[ZongCallRecord]:
        if not start_date or not end_date:
            end_date = datetime.datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.datetime.now() - datetime.timedelta(days=settings.zong_default_days)).strftime("%Y-%m-%d")

        form_data = {
            "vpbx_id": self.vpbx_id,
            "token": self.token,
            "startDate": start_date,
            "endDate": end_date
        }

        try:
            response = self.session.post(self.base_url, data=form_data)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and data.get("status") and data.get("code") == 200:
                return [ZongCallRecord(**record) for record in data.get("data", [])]
            return []
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Zong API error: {str(e)}")