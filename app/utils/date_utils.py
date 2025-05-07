from datetime import datetime

def parse_clickup_date(date_value):
    """Parse ClickUp date values in various formats"""
    if isinstance(date_value, (int, float)):
        return datetime.fromtimestamp(date_value/1000)
    elif isinstance(date_value, str):
        if date_value.isdigit():
            return datetime.fromtimestamp(int(date_value)/1000)
        elif 'T' in date_value:
            return datetime.fromisoformat(date_value.split('T')[0])
        else:
            return datetime.strptime(date_value, '%Y-%m-%d')
    raise ValueError(f"Unsupported date format: {date_value}")