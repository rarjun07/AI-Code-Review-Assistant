from fastapi import FastAPI

from app.database import Base, engine
from app.models import User
from app.routes.auth import router as auth_router
from app.routes.upload import upload_code_file
from fastapi.middleware.cors import CORSMiddleware
from app.routes.upload import upload_code_file, get_upload_history
from app.routes.reports import get_report_by_id, get_reports
app = FastAPI(
    title="AI Code Review Assistant",
    description="AI-powered Code Review Assistant built with FastAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.post("/upload/code", tags=["Upload"])(upload_code_file)
app.get("/upload/history", tags=["Upload"])(get_upload_history)



app.get("/reports", tags=["Reports"])(get_reports)
app.get("/reports/{report_id}", tags=["Reports"])(get_report_by_id)


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