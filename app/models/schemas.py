from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional,Union, Dict


class CallRecord(BaseModel):
    customer_number: str
    prefix: str
    duration: int
    extension: str
    call_type: str
    call_response: str
    time: str
    recording: Optional[str] = None

class CallStatsResponse(BaseModel):
    total_calls: int
    connected_calls: int
    not_attended_calls: int
    other_status_calls: int
    connection_rate: float
    avg_duration: float
    calls_by_extension: dict

class PaginatedResponse(BaseModel):
    metadata: dict
    data: list

class CallResponseWithCount(BaseModel):
    calls: List[CallRecord]
    total_count: int
    description: str

class FeedbackEntry(BaseModel):
    name: str
    nps: Optional[float]
    comment: Optional[str]
    task_url: str

class DailyFeedback(BaseModel):
    date: str
    total_entries: int
    avg_nps: Optional[float]
    entries: List[FeedbackEntry]

class FeedbackReport(BaseModel):
    total_feedback_calls: int
    daily_breakdown: List[DailyFeedback]


class DailyPendingTasks(BaseModel):
    date: str
    pending_calls: int


class PendingTasksResponse(BaseModel):
    total_pending_calls: int
    date_wise: List[DailyPendingTasks]

class PaymentEntry(BaseModel):
    name: str
    payable: float
    received: float
    remaining: float
    url: str

class DailyReport(BaseModel):
    date: date
    installations: int
    total_payable: float
    total_received: float

class PaymentReportResponse(BaseModel):
    total_installations: int
    total_amount_payable: float
    total_amount_received: float
    total_amount_remaining: float
    daily_breakdown: List[DailyReport]

class ConvertedCall(BaseModel):
    call_id: Optional[str]
    phone_number: str
    normalized_phone: str
    call_time: str
    duration: int
    customer_name: str = Field(default="Unknown Customer")
    clickup_task_url: Optional[str]
    call_date: date

class AnalysisResult(BaseModel):
    total_converted_calls: int
    conversion_rate: Optional[float]
    converted_calls: List[ConvertedCall]
    daily_breakdown: Dict[date, int]
    time_period: dict

class ZongCallRecord(BaseModel):
    customer_number: Optional[str] = None
    call_type: Optional[str] = None
    duration: Optional[Union[str, int]] = Field(None)  # Accepts both string and int
    time: Optional[str] = None
    # Add other fields with proper Optional typing

class ClickUpTask(BaseModel):
    id: str
    name: str
    url: str
    custom_fields: Optional[List[Dict]] = None

class MatchedResult(BaseModel):
    task_id: str
    task_name: str
    task_url: str
    phone: Optional[str] = None
    zong_call: ZongCallRecord

class DateRange(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None