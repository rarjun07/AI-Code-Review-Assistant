from fastapi import FastAPI

app = FastAPI(
    title="AI Code Review Assistant",
    description="AI-powered Code Review Assistant built with FastAPI",
    version="1.0.0",
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