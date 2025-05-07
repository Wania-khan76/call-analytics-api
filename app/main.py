from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.surveys import router as surveys_router
from app.api.ckickup_api_routes import router as clickup_router
from app.api.feedback import router as feedback_router
from app.api import endpoints, converted_calls
from app.api.B2B import router as integration_router

app = FastAPI(
    title="Call Analytics API",
    version="1.0.0",
    openapi_url="/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(api_router, prefix="/api/v1")
app.include_router(surveys_router,prefix="/api/v1")
app.include_router(clickup_router, prefix="/api/v1")
app.include_router(feedback_router,prefix="/api/v1")
app.include_router(converted_calls.router,prefix="/api/v1")
app.include_router(integration_router)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


