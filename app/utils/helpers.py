from datetime import datetime, date
from typing import List, Dict, Optional
import re
from app.core.config import settings

def format_duration(seconds: int) -> str:
    """
    Convert seconds to MM:SS format
    Example: 125 -> "2:05"
    """
    if not isinstance(seconds, (int, float)) or seconds < 0:
        return "0:00"
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}:{secs:02d}"

def format_phone_number(number: str) -> str:
    """
    Format phone numbers consistently
    Example: "03301234567" -> "0301 234567"
    """
    if not number:
        return ""
    cleaned = re.sub(r'[^\d]', '', number)
    if len(cleaned) == 11 and cleaned.startswith('0'):
        return f"{cleaned[:4]} {cleaned[4:]}"
    return number

def parse_date(date_str: str, fmt: str = "%Y-%m-%d") -> Optional[date]:
    """
    Safely parse date strings with format validation
    Returns None if invalid
    """
    try:
        return datetime.strptime(date_str, fmt).date()
    except (ValueError, TypeError):
        return None

def calculate_percentage(numerator: float, denominator: float) -> float:
    """
    Safe percentage calculation with zero division guard
    Returns 0.0 if denominator is 0
    """
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)

def filter_dict_list(data: List[Dict], filters: Dict) -> List[Dict]:
    """
    Filter list of dictionaries by key-value pairs
    Example: 
        filter_dict_list(calls, {'call_type': 'outbound'})
    """
    return [
        item for item in data
        if all(item.get(key) == value for key, value in filters.items())
    ]

def group_by_key(data: List[Dict], key: str) -> Dict:
    """
    Group dictionary list by a specific key
    Returns: {key_value1: [items], key_value2: [items]}
    """
    grouped = {}
    for item in data:
        group_key = item.get(key)
        if group_key not in grouped:
            grouped[group_key] = []
        grouped[group_key].append(item)
    return grouped

def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validate that start_date <= end_date
    Returns True if valid, False otherwise
    """
    return start_date <= end_date if start_date and end_date else False


from datetime import datetime, date
import re

def normalize_phone_number(phone: str) -> str:
    """Normalize phone numbers to digits only"""
    if not phone:
        return ""
    # Remove all non-digit characters and international prefixes
    normalized = re.sub(r'[^\d]', '', phone)
    # Keep last 10 digits (remove country code if present)
    return normalized[-10:]

def extract_phone_from_lead(lead: dict) -> str:
    """Extract phone number from ClickUp task custom fields"""
    custom_fields = lead.get('custom_fields', [])
    
    # Try multiple possible field names
    phone_field_names = ['Phone', 'phone', 'phone_number', 'Primary Phone', 'Contact Number']
    
    for field in custom_fields:
        field_name = field.get('name', '').lower()
        field_value = field.get('value', '')
        
        # Check if field matches any known phone field names
        if any(name.lower() in field_name for name in phone_field_names):
            if field_value:
                return normalize_phone_number(str(field_value))
        
        # Additional check for field ID if known
        if field.get('id') == '5cadcca7-5ec9-4f26-8ee6-b6939662608a':  # Your Primary Phone field ID
            if field_value:
                return normalize_phone_number(str(field_value))
    
    return ""

def extract_name_from_lead(lead: dict) -> str:
    """Extract customer name from ClickUp task"""
    return lead.get('name', 'Unknown Customer')

def parse_call_date(call_time: str) -> date:
    """Parse various date formats from call records"""
    try:
        if 'T' in call_time:  # ISO format
            return datetime.fromisoformat(call_time.replace('Z', '')).date()
        if 'AM' in call_time or 'PM' in call_time:  # 12-hour format
            return datetime.strptime(call_time, "%Y-%m-%d %I:%M:%S %p").date()
        return datetime.strptime(call_time, "%Y-%m-%d %H:%M:%S").date()  # 24-hour format
    except (ValueError, AttributeError):
        return datetime.now().date()