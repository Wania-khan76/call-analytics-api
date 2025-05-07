from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class Survey(BaseModel):
    id: str
    name: str
    status: str
    survey_date: date
    url: str
    list_name: Optional[str] = None


class DailySurveyCount(BaseModel):
    date: date
    count: int
