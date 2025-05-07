
from fastapi import APIRouter, HTTPException
from datetime import date
from typing import List
from app.services.survey_service import SurveyService
from app.models.survey import DailySurveyCount
import logging
from fastapi import Query


logger = logging.getLogger(__name__)

router = APIRouter()

survey_service = SurveyService()


@router.get("/last-week", response_model=List[DailySurveyCount])
async def get_surveys_last_week():
    """Get survey counts for last 7 days"""
    return SurveyService().get_surveys_for_period(days=7)

@router.get("/by-date-range", response_model=List[DailySurveyCount])
async def get_surveys_by_date_range(start: str, end: str):
    """Get surveys for custom date range (YYYY-MM-DD format)"""
    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    if (end_date - start_date).days > 60:
        raise HTTPException(400, "Date range too large (max 60 days)")
        
    return SurveyService().get_surveys_for_period(start_date=start_date, end_date=end_date)

@router.get("/today", response_model=DailySurveyCount)
async def get_surveys_today():
    """Get today's survey count"""
    today_data = SurveyService().get_surveys_for_period(days=1)
    return today_data[0] if today_data else DailySurveyCount(date=date.today(), count=0, surveys=[])

@router.get("/surveys-by-end-date", response_model=List[DailySurveyCount])
async def get_surveys_by_end_date(
    end_date: date = Query(...)
):
    try:
        # Set start_date automatically to 30 days before the end_date
        start_date = end_date - timedelta(days=29)  # 30 days including end_date
        
        logger.info(f"Fetching surveys from {start_date} to {end_date}")
        
        surveys = survey_service.get_surveys_for_period(
            start_date=start_date,
            end_date=end_date
        )
        
        return surveys
    except Exception as e:
        logger.error(f"Error fetching surveys by end date: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch survey data.")