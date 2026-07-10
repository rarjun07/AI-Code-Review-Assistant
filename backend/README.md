# Backend

This folder contains the FastAPI backend for the AI Code Review Assistant.


## Tech Stack

- FastAPI
- Python
- Pydantic
- Uvicorn
- OpenAI API


## Environment

Create a `.env` file in this backend folder.

```env
DATABASE_URL=postgresql://username:password@localhost:5432/ai_code_review_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

  
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
