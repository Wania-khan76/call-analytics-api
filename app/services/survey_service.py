
from datetime import date, timedelta, datetime
from typing import List, Dict, Any
from app.core.clickup_client import ClickUpClient
from app.models.survey import Survey, DailySurveyCount
import logging
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class SurveyService:
    def __init__(self):
        self.client = ClickUpClient()

        # Initialize required attributes
        self.survey_date_field_id = settings.SURVEY_DATE_FIELD_ID  # From your config

    def get_surveys_for_period(self, days: int = 7, start_date: date = None, end_date: date = None) -> List[DailySurveyCount]:
        # Convert to datetime at start of day
        if start_date and end_date:
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.max.time())
        else:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days-1)

        # Get date range for final grouping
        date_range = self._generate_date_range(start_dt.date(), end_dt.date())

        try:
            all_tasks = self.client.get_survey_tasks_by_date_range(start_dt)
            logger.info(f"Found {len(all_tasks)} total tasks across all lists")
        
            # Create a dictionary to count surveys by date
            date_counts = {}
            for task in all_tasks:
                try:
                    survey = self._map_to_survey(task)
                    if survey:
                        date_counts[survey.survey_date] = date_counts.get(survey.survey_date, 0) + 1
                except Exception as e:
                    logger.error(f"Error processing task {task.get('id')}: {e}")
                    continue
        
            # Create results for all dates in range, even if count is 0
            results = []
            for single_date in date_range:
                count = date_counts.get(single_date, 0)
                results.append(DailySurveyCount(
                    date=single_date,
                    count=count
                ))
        
            return results
        except Exception as e:
            logger.error(f"Error in get_surveys_for_period: {e}")
            raise

    def _generate_date_range(self, start_date: date, end_date: date) -> List[date]:
        delta = (end_date - start_date).days + 1
        return [start_date + timedelta(days=i) for i in range(delta)]


    def _map_to_survey(self, task: Dict[str, Any]) -> Optional[Survey]:
        """Convert ClickUp task to Survey model with proper timestamp handling"""
        try:
            custom_fields = task.get('custom_fields', [])
            survey_date = None
            # phone_number = None
        
            for field in custom_fields:
                if str(field.get('id')) == self.survey_date_field_id:
                    # Handle both ISO strings and millisecond timestamps
                    field_value = field.get('value')
                    if not field_value:
                        continue
                    
                    try:
                        # First try parsing as milliseconds timestamp
                        timestamp_ms = int(field_value)
                        survey_date = datetime.fromtimestamp(timestamp_ms/1000).date()
                    except (ValueError, TypeError):
                        # Fall back to ISO format parsing
                        try:
                            survey_date = date.fromisoformat(field_value)
                        except ValueError:
                            logger.warning(f"Unparseable date format in task {task.get('id')}: {field_value}")
                            continue
        
            if not survey_date:
                return None
            
            return Survey(
                id=task.get('id', ''),
                name=task.get('name', ''),
                status=task.get('status', {}).get('status', ''),
                survey_date=survey_date,
                url=task.get('url', '')
            )
        except Exception as e:
            logger.error(f"Error mapping task {task.get('id')}: {e}")
            return None







