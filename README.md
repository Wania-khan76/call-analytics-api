# Call Analytics API

A FastAPI-based service for fetching and analyzing call, survey, feedback, and payment data from Zong and ClickUp APIs.

## Features

- Fetch connected, outbound, and converted call analytics
- Survey analytics (last week, by date range, today, by end date)
- Feedback reporting
- Payment and pending task reporting
- Modular, extensible architecture
- Swagger UI and ReDoc documentation
- Environment-based configuration

## Project Structure

```
app/
├── main.py                # FastAPI app setup and router inclusion
├── api/                   # API route handlers
│   ├── endpoints.py       # Call analytics endpoints
│   ├── converted_calls.py # Converted calls analysis
│   ├── surveys.py         # Survey analytics endpoints
│   ├── feedback.py        # Feedback endpoints
│   ├── ckickup_api_routes.py # ClickUp and payment endpoints
│   └── ...
├── services/              # Business logic/services
│   ├── call_service.py    # Call analytics logic
│   ├── survey_service.py  # Survey analytics logic
│   ├── feedback_service.py# Feedback logic
│   ├── payment_service.py # Payment logic
│   └── ...
├── models/                # Pydantic schemas/models
│   ├── schemas.py         # Main data models
│   └── survey.py          # Survey models
├── core/                  # Core config and clients
│   ├── config.py          # Settings and environment
│   └── clickup_client.py  # ClickUp API client
├── external/              # External API clients
│   ├── zong_api.py        # Zong API client
│   └── ...
├── utils/                 # Utility functions
│   ├── helpers.py         # Helper functions
│   └── date_utils.py      # Date utilities
├── __init__.py
requirements.txt           # Python dependencies
.env                       # Environment variables (not committed)
README.md                  # This documentation
```

## Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   Create a `.env` file in the project root with the following (see `app/core/config.py` for all options):
   ```env
   VPBX_ID=your_vpbx_id
   ZONG_API_TOKEN=your_zong_api_token
   ZONG_API_URL=https://cap.zong.com.pk:8444/vpbx-apis/customApi/vpbx-custom-apis
   CLICKUP_API_KEY=your_clickup_api_key
   CLICKUP_TEAM_ID=your_clickup_team_id
   SURVEY_DATE_FIELD_ID=your_survey_date_field_id
   CLICKUP_API_URL=https://api.clickup.com/api/v2/
   # ...other fields as needed
   ```

3. **Run the API**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Requirements

- Python 3.8+
- fastapi==0.111.0
- uvicorn==0.29.0
- pydantic-settings==2.2.1
- pydantic==2.7.1
- requests==2.32.3
- python-dotenv==1.0.1
- pandas==2.2.3

## Configuration

All configuration is managed via environment variables (see `.env` and `app/core/config.py`). Sensitive keys (API tokens, etc.) should never be committed to version control.

## API Endpoints Overview

### Health Check
- `GET /health` — Returns `{"status": "healthy"}`

### Call Analytics
- `GET /api/v1/connected-calls?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — List all connected calls
- `GET /api/v1/outbound-calls?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — List all outbound calls
- `GET /api/v1/connected-outbound-calls?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — List all connected outbound calls

**Response Example:**
```json
{
  "calls": [
    {
      "customer_number": "string",
      "prefix": "string",
      "duration": 0,
      "extension": "string",
      "call_type": "string",
      "call_response": "string",
      "time": "string",
      "recording": "string"
    }
  ],
  "total_count": 1,
  "description": "All calls with 'Connected' status"
}
```

### Converted Calls Analysis
- `GET /api/v1/converted-calls/analysis?days=30` — Analyze converted calls for the last N days

### Survey Analytics
- `GET /api/v1/last-week` — Survey counts for last 7 days
- `GET /api/v1/by-date-range?start=YYYY-MM-DD&end=YYYY-MM-DD` — Surveys for a custom date range
- `GET /api/v1/today` — Today's survey count
- `GET /api/v1/surveys-by-end-date?end_date=YYYY-MM-DD` — Surveys for the 30 days up to end_date

### Feedback
- `GET /api/v1/feedback?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — Feedback report for a date range

### ClickUp/Payment APIs
- `GET /api/v1/total-survey?date=YYYY-MM-DD` — Total survey count for 30 days up to date
- `GET /api/v1/installed-survey?date=YYYY-MM-DD` — Installed survey stats for 30 days up to date
- `GET /api/v1/pending-tasks?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — Pending tasks report
- `GET /api/v1/payments-report?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — Payments report

## Data Models (Schemas)

- **CallRecord**: Call details (number, duration, type, etc.)
- **CallResponseWithCount**: List of calls, total count, description
- **AnalysisResult**: Converted calls analysis (total, rate, breakdown)
- **FeedbackReport**: Feedback summary and daily breakdown
- **PendingTasksResponse**: Pending calls summary
- **PaymentReportResponse**: Payment stats and daily breakdown
- **DailySurveyCount**: Survey stats per day

See `app/models/schemas.py` for full details.

## Example Usage

**Python:**
```python
import requests
response = requests.get(
    "http://localhost:8000/api/v1/connected-calls",
    params={"start_date": "2025-04-01", "end_date": "2025-04-21"}
)
data = response.json()
print(f"Total connected calls: {data['total_count']}")
```

**cURL:**
```bash
curl "http://localhost:8000/api/v1/connected-calls?start_date=2025-04-01&end_date=2025-04-21"
```

## Error Handling

- 200: Success
- 400: Invalid request (e.g., bad date format)
- 500: Server error (with error message)

## License

[MIT](https://choosealicense.com/licenses/mit/)