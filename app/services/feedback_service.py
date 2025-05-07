import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from app.models.schemas import FeedbackEntry, DailyFeedback, FeedbackReport
from app.external.clickup_client import extract_custom_field, FIELD_FEEDBACK_DATE, FIELD_FEEDBACK_NPS, FIELD_FEEDBACK_COMMENTS
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def generate_feedback_report(tasks: List[Dict]) -> FeedbackReport:
    feedback_by_date = defaultdict(list)

    logger.info(f"Generating feedback report for {len(tasks)} tasks")

    for task in tasks:
        feedback_ts = extract_custom_field(task, FIELD_FEEDBACK_DATE)
        if not feedback_ts:
            continue

        try:
            feedback_ts = int(feedback_ts)
            date_str = datetime.datetime.fromtimestamp(feedback_ts / 1000).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            continue

        nps = extract_custom_field(task, FIELD_FEEDBACK_NPS)
        comment = extract_custom_field(task, FIELD_FEEDBACK_COMMENTS)

        clean_nps = None
        if nps is not None:
            try:
                clean_nps = float(nps)
                if not (0 <= clean_nps <= 10):
                    clean_nps = None
            except (ValueError, TypeError):
                clean_nps = None

        feedback_by_date[date_str].append({
            'name': task.get('name', 'N/A'),
            'nps': clean_nps,
            'comment': comment,
            'task_url': task.get('url', 'N/A')
        })

    daily_breakdown = []
    for date in sorted(feedback_by_date.keys()):
        entries = feedback_by_date[date]
        valid_nps = [e['nps'] for e in entries if e['nps'] is not None]
        avg_nps = sum(valid_nps) / len(valid_nps) if valid_nps else None

        daily_breakdown.append(DailyFeedback(
            date=date,
            total_entries=len(entries),
            avg_nps=round(avg_nps, 1) if avg_nps is not None else None,
            entries=[FeedbackEntry(**e) for e in entries]
        ))

    total = sum(len(entries) for entries in feedback_by_date.values())

    logger.info(f"Generated report with {total} total feedback entries.")

    return FeedbackReport(
        total_feedback_calls=total,
        daily_breakdown=daily_breakdown
    )


