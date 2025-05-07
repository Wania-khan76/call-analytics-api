from datetime import date
from typing import List
from app.external.zong_api import ZongAPIClient
from app.models.schemas import CallRecord

class CallService:
    @staticmethod
    def get_connected_calls(start_date: date, end_date: date) -> List[CallRecord]:
        return ZongAPIClient.fetch_connected_calls(start_date, end_date)
    
    @staticmethod
    def get_outbound_calls(start_date: date, end_date: date) -> List[CallRecord]:
        return ZongAPIClient.fetch_outbound_calls(start_date, end_date)
    
    @staticmethod
    def get_connected_outbound_calls(start_date: date, end_date: date) -> List[CallRecord]:
        return ZongAPIClient.fetch_connected_outbound_calls(start_date, end_date)

