

import requests
import urllib3
from datetime import datetime
from fastapi import HTTPException
from app.core.config import settings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ZongService:
    @staticmethod
    def _make_request(start_date: str, end_date: str) -> dict:
        """Base method to make API request"""
        payload = {
            "vpbx_id": settings.vpbx_id,
            "token": settings.zong_api_token,
            "start_date": start_date,
            "end_date": end_date
        }
        
        try:
            response = requests.post(
                settings.zong_api_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                verify=False
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Zong API Error: {str(e)}"
            )

    async def fetch_outbound_calls(self, start_date: datetime, end_date: datetime) -> list:
        """Fetch outbound connected calls from Zong API"""
        data = self._make_request(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        return [
            {
                'id': call.get('id'),
                'phone_number': call.get('customer_number'),
                'duration': call.get('duration'),
                'timestamp': call.get('time'),
                'direction': 'outbound',
                'status': 'connected'
            }
            for call in data.get('data', [])
            if (call.get('call_type', '').lower() == 'outbound' and 
                call.get('call_response') == 'Connected')
        ]

# Create the service instance
zong_service = ZongService()