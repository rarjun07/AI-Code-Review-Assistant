from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.auth import router as auth_router
from app.routes.reports import (
    delete_report,
    export_report,
    get_report_by_id,
    get_reports,
)
from app.routes.upload import get_upload_history, upload_code_file

app = FastAPI(
    title="AI Code Review Assistant",
    description="AI-powered Code Review Assistant built with FastAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.post("/upload/code", tags=["Upload"])(upload_code_file)
app.get("/upload/history", tags=["Upload"])(get_upload_history)


app.get("/reports", tags=["Reports"])(get_reports)
app.get("/reports/{report_id}", tags=["Reports"])(get_report_by_id)
app.delete("/reports/{report_id}", tags=["Reports"])(delete_report)
app.get("/reports/{report_id}/export/{export_format}", tags=["Reports"])(
    export_report
)


@app.get("/")
def root():
    return {
        "message": "Welcome to AI Code Review Assistant 🚀"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
