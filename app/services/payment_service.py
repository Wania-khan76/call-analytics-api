import requests
from datetime import datetime, date, timedelta
from collections import defaultdict
from app.core.config import settings
from app.models.schemas import PaymentReportResponse, DailyReport, PaymentEntry
from app.utils.date_utils import parse_clickup_date

# Field IDs
FIELD_INSTALLATION_DATE = settings.INSTALLED_DATE_FIELD_ID
FIELD_AMOUNT_PAYABLE = settings.AMOUNT_PAYABLE_FIELD_ID
FIELD_AMOUNT_RECEIVED = settings.AMOUNT_RECEIVED_FIELD_ID
CLICKUP_LIST_ID=901802098213
async def get_payment_report(start_date: date = None, end_date: date = None):
    """Main service function to generate payment report"""
    # Set default dates if not provided
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    
    # Get and filter tasks
    tasks = await _get_all_tasks()
    filtered_tasks = _filter_tasks_by_date(tasks, start_date, end_date)
    
    # Generate report
    report_data = _generate_report_data(filtered_tasks)
    
    # Convert to response model - use the correct format function
    return _format_report_response(report_data)  # Changed this line

def _format_report_response(report_data):  # Renamed this function
    """Format the final API response"""
    daily_reports = []
    total_installations = 0
    total_payable = 0.0
    total_received = 0.0
    
    for date_str in sorted(report_data.keys()):
        entries = report_data[date_str]
        daily_payable = sum(e['payable'] for e in entries)
        daily_received = sum(e['received'] for e in entries)
        
        daily_reports.append(DailyReport(
            date=datetime.strptime(date_str, '%Y-%m-%d').date(),
            installations=len(entries),
            total_payable=daily_payable,
            total_received=daily_received
        ))
        
        total_installations += len(entries)
        total_payable += daily_payable
        total_received += daily_received
    
    return PaymentReportResponse(
        total_installations=total_installations,
        total_amount_payable=total_payable,
        total_amount_received=total_received,
        total_amount_remaining=total_payable - total_received,
        daily_breakdown=daily_reports
    )



async def _get_all_tasks():
    """Fetch all tasks from ClickUp"""
    all_tasks = []
    page = 0
    
    while True:
        url = f"https://api.clickup.com/api/v2/list/{settings.CLICKUP_LIST_ID}/task"
        params = {'page': page, 'include_closed': 'true'}
        
        response = requests.get(
            url,
            headers={'Authorization': settings.CLICKUP_API_KEY},
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"ClickUp API error: {response.text}")
            
        data = response.json()
        tasks = data.get('tasks', [])
        if not tasks:
            break
            
        all_tasks.extend(tasks)
        page += 1
        
        if page > 20:  # Safety limit
            break
            
    return all_tasks

def _filter_tasks_by_date(tasks, start_date, end_date):
    """Filter tasks by date range"""
    filtered = []
    
    for task in tasks:
        date_value = None
        for field in task.get('custom_fields', []):
            if str(field.get('id')) == FIELD_INSTALLATION_DATE:
                date_value = field.get('value')
                break
                
        if not date_value:
            continue
            
        try:
            task_date = parse_clickup_date(date_value)
            if start_date <= task_date.date() <= end_date:
                filtered.append(task)
        except Exception as e:
            continue
            
    return filtered

def _generate_report_data(tasks):
    """Generate report data structure"""
    report = defaultdict(list)
    
    for task in tasks:
        payable = 0
        received = 0
        date_str = ""
        
        for field in task.get('custom_fields', []):
            field_id = str(field.get('id'))
            value = field.get('value')
            
            if field_id == FIELD_INSTALLATION_DATE and value:
                task_date = parse_clickup_date(value)
                date_str = task_date.strftime('%Y-%m-%d')
            elif field_id == FIELD_AMOUNT_PAYABLE and value:
                try: payable = float(value)
                except: pass
            elif field_id == FIELD_AMOUNT_RECEIVED and value:
                try: received = float(value)
                except: pass
        
        if date_str:
            report[date_str].append({
                'name': task.get('name', 'N/A'),
                'payable': payable,
                'received': received,
                'remaining': payable - received,
                'url': task.get('url', 'N/A')
            })
    
    return report

