
from fastapi import APIRouter, HTTPException
from typing import Optional
import datetime
from app.services.feedback_service import generate_feedback_report
from app.external.clickup_client import fetch_feedback_tasks
from app.models.schemas import FeedbackReport

router = APIRouter()

@router.get("/feedback", response_model=FeedbackReport)
async def get_feedback_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Endpoint to get feedback report for a date range"""
    today = datetime.date.today()
    start_date = start_date or (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = end_date or today.strftime('%Y-%m-%d')

    try:
        # Fetch feedback tasks concurrently
        tasks = await fetch_feedback_tasks(start_date, end_date)
        # Generate the feedback report concurrently
        report = await generate_feedback_report(tasks)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
