


from datetime import datetime, timedelta, date
from fastapi import APIRouter, HTTPException
from app.services import zong, clickup
from app.utils.helpers import (
    normalize_phone_number,
    extract_phone_from_lead,
    extract_name_from_lead,
    parse_call_date
)
from app.models.schemas import AnalysisResult, ConvertedCall
from app.core.config import settings
from collections import defaultdict
import logging
# In your endpoint file, change the import to:
from app.services.zong import zong_service as zong

router = APIRouter(prefix="/converted-calls", tags=["Converted Calls Analysis"])
logger = logging.getLogger(__name__)

@router.get("/analysis", response_model=AnalysisResult)
async def analyze_converted_calls(days: int = settings.days_to_fetch):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Fetching data from {start_date} to {end_date}")
        
        # Fetch data from both APIs
        outbound_calls = await zong.fetch_outbound_calls(start_date, end_date)
        installed_leads = await clickup.fetch_installed_leads(start_date, end_date)
        
        logger.info(f"Found {len(outbound_calls)} outbound calls and {len(installed_leads)} leads")
        
        # Build phone to lead mapping
        phone_to_lead = {}
        for lead in installed_leads:
            phone = extract_phone_from_lead(lead)
            if phone:
                phone_to_lead[phone] = {
                    'name': extract_name_from_lead(lead),
                    'url': lead.get('url')
                }
        
        logger.info(f"Found {len(phone_to_lead)} leads with valid phone numbers")
        
        # Match calls to leads
        converted_calls = []
        daily_counts = defaultdict(int)
        
        for call in outbound_calls:
            call_phone = normalize_phone_number(call.get('phone_number', ''))
            if not call_phone:
                continue
                
            matched_lead = phone_to_lead.get(call_phone)
            if matched_lead:
                call_date = parse_call_date(call.get('timestamp'))
                converted_call = ConvertedCall(
                    call_id=call.get('id'),
                    phone_number=call.get('phone_number'),
                    normalized_phone=call_phone,
                    call_time=call.get('timestamp'),
                    duration=call.get('duration'),
                    customer_name=matched_lead['name'],
                    clickup_task_url=matched_lead['url'],
                    call_date=call_date
                )
                converted_calls.append(converted_call)
                daily_counts[call_date] += 1
        
        logger.info(f"Found {len(converted_calls)} converted calls")
        
        # Fill in dates with zero counts
        complete_daily_breakdown = {}
        current_date = start_date.date()
        while current_date <= end_date.date():
            complete_daily_breakdown[current_date] = daily_counts.get(current_date, 0)
            current_date += timedelta(days=1)
        
        # Calculate conversion rate
        conversion_rate = round(
            (len(converted_calls) / len(outbound_calls) * 100) if outbound_calls else 0,
            2
        )
        
        return AnalysisResult(
            total_converted_calls=len(converted_calls),
            conversion_rate=conversion_rate,
            converted_calls=converted_calls,
            daily_breakdown=complete_daily_breakdown,
            time_period={
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )