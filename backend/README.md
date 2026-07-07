# Backend

This folder contains the FastAPI backend for the AI Code Review Assistant.


## Tech Stack

- FastAPI
- Python
- Pydantic
- Uvicorn

  
## Run

```bash
cd backend

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```
