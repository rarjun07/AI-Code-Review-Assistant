from fastapi import FastAPI
from app.database import Base, engine
from app.models import User
from app.routes.auth import router as auth_router

app = FastAPI(
    title="AI Code Review Assistant",
    description="AI-powered Code Review Assistant built with FastAPI",
    version="1.0.0",
)


# Create the database tables
Base.metadata.create_all(bind=engine)
app.include_router(auth_router)

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