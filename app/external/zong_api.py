import requests
import urllib3
from typing import List, Dict
from app.core.config import settings
from datetime import date

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ZongAPIClient:
    @staticmethod
    def _make_request(start_date: str, end_date: str) -> Dict:
        """Base method to make API request"""
        payload = {
            "vpbx_id": settings.vpbx_id,
            "token": settings.zong_api_token,
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = requests.post(
            settings.zong_api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            verify=False
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def fetch_connected_calls(start_date: date, end_date: date) -> List[Dict]:
        """Fetch only calls with 'Connected' status"""
        data = ZongAPIClient._make_request(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        return [
            call for call in data.get('data', [])
            if call.get('call_response') == 'Connected'
        ]

    @staticmethod
    def fetch_outbound_calls(start_date: date, end_date: date) -> List[Dict]:
        """Fetch all outbound calls regardless of status"""
        data = ZongAPIClient._make_request(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        return [
            call for call in data.get('data', [])
            if call.get('call_type', '').lower() == 'outbound'
        ]

    @staticmethod
    def fetch_connected_outbound_calls(start_date: date, end_date: date) -> List[Dict]:
        """Fetch only outbound calls with 'Connected' status"""
        data = ZongAPIClient._make_request(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        return [
            call for call in data.get('data', [])
            if (call.get('call_type', '').lower() == 'outbound' and 
                call.get('call_response') == 'Connected')
        ]