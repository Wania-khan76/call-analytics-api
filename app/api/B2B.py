# app/api/endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.services.B2Bzong import ZongService
from app.services.B2Bclickup import ClickUpService
from app.services.B2Bcomparator import DataComparator
from app.models.schemas import MatchedResult, DateRange
from app.core.config import settings

router = APIRouter(
    prefix="/api/v1/integration",
    tags=["integration"]
)

@router.post("/compare", response_model=List[MatchedResult])
async def compare_data(
    date_range: Optional[DateRange] = None,
    zong_service: ZongService = Depends(ZongService),
    clickup_service: ClickUpService = Depends(ClickUpService),
    comparator: DataComparator = Depends(DataComparator)
):
    """
    Compare Zong call records with ClickUp tasks tagged as 'potential b2b'
    """
    try:
        # Get data from services
        zong_data = zong_service.get_call_records(
            date_range.start_date if date_range else None,
            date_range.end_date if date_range else None
        )
        clickup_tasks = clickup_service.get_tasks_by_tag(
            list_ids=settings.clickup_list_ids_list,  # Use the list property
            tag_name="potential b2b"
        )
        
        # Compare data
        return comparator.compare_data(zong_data, clickup_tasks)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Explicitly export the router
__all__ = ["router"]