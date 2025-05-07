from fastapi import APIRouter, Query, HTTPException
from datetime import date, timedelta
from app.services.call_service import CallService
from app.models.schemas import CallResponseWithCount, CallRecord


from datetime import datetime
import logging
# from app.utils.date_utils import parse_date_input

logger = logging.getLogger(__name__)


router = APIRouter()

@router.get("/connectedd-calls", response_model=CallResponseWithCount)
async def get_connected_calls(
    start_date: date = Query(...),
    end_date: date = Query(...)
):
    calls = CallService.get_connected_calls(start_date, end_date)
    return {
        "calls": calls,
        "total_count": len(calls),
        "description": "All calls with 'Connected' status"
    }

@router.get("/outbound-calls", response_model=CallResponseWithCount)
async def get_outbound_calls(
    start_date: date = Query(...),
    end_date: date = Query(...)
):
    calls = CallService.get_outbound_calls(start_date, end_date)
    return {
        "calls": calls,
        "total_count": len(calls),
        "description": "All outbound calls"
    }

@router.get("/connected-outbound-calls", response_model=CallResponseWithCount)
async def get_connected_outbound_calls(
    start_date: date = Query(...),
    end_date: date = Query(...)
):
    calls = CallService.get_connected_outbound_calls(start_date, end_date)
    return {
        "calls": calls,
        "total_count": len(calls),
        "description": "Outbound calls with 'Connected' status"
    }


