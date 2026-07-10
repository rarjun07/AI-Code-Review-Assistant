#  AI Code Review Assistant

AI Code Review Assistant is an AI-powered full-stack web application that helps developers and students automatically analyze Python source code.

The application combines **static code analysis** and **AI-powered review** to detect code quality issues, security vulnerabilities, complexity, and maintainability.

---

#  Project Objective

The objective of this project is to build a production-ready AI Code Review platform using modern full-stack technologies.

Users can:

- Register and login securely
- Upload Python (.py) files
- Analyze code using multiple analysis tools
- View previous reports
- Review code with AI-powered recommendations using OpenAI

---

#  Features

## Authentication

- User Registration
- User Login
- JWT Authentication
- Protected API Routes

---

## File Upload

- Upload Python (.py) files
- Secure upload endpoint
- Store uploaded files
- Upload history

---

## Static Code Analysis

### Pylint

Checks:

- Code Quality
- Coding Standards
- Errors
- Warnings
- Conventions

---

### Bandit

Checks:

- Security Vulnerabilities
- Unsafe Functions
- Dangerous Python Patterns

---

### Radon

Checks:

- Cyclomatic Complexity
- Maintainability Index

---

## Reports

- Save reports in PostgreSQL
- Report History
- View previous reports
- Report Summary
- Security Summary
- Complexity Summary

---

# 🛠 Tech Stack

## Backend

- FastAPI
- Python
- SQLAlchemy
- PostgreSQL
- JWT Authentication

---

## Frontend

- React.js
- React Router
- Axios
- HTML5
- CSS3
- JavaScript (ES6+)

---

## Static Analysis

- Pylint
- Bandit
- Radon

---

## AI

- OpenAI API

---

#  Project Structure

```text
AI-Code-Review-Assistant/

backend/
│
├── app/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── upload.py
│   │   └── analysis_report.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── upload.py
│   │   └── reports.py
│   │
│   ├── schemas/
│   ├── services/
│   │   ├── pylint_service.py
│   │   ├── bandit_service.py
│   │   └── radon_service.py
│   │
│   ├── utils/
│   └── uploads/
│
└── requirements.txt

frontend/
│
├── src/
│   ├── layouts/
│   ├── pages/
│   ├── routes/
│   ├── services/
│   ├── App.jsx
│   └── main.jsx
│
└── package.json
```

---

#  Database Tables

- users
- uploaded_files
- analysis_reports

---

#  API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Welcome API |
| GET | `/health` | Health Check |
| POST | `/auth/register` | Register User |
| POST | `/auth/login` | User Login |
| GET | `/auth/me` | Current User |
| POST | `/upload/code` | Upload & Analyze Python File |
| GET | `/upload/history` | Upload History |
| GET | `/reports` | List Saved Reports |
| GET | `/reports/{report_id}` | Report Details |

---

# ⚙ Environment Variables

Create a `.env` file inside the backend directory.

```env
DATABASE_URL=postgresql://username:password@localhost/ai_code_review_db

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

OPENAI_API_KEY=your_openai_api_key_here

OPENAI_MODEL=gpt-4.1-mini
```

---

# ▶ Running the Backend

```bash
cd backend

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend:

```
http://127.0.0.1:8000
```

Swagger:

```
http://127.0.0.1:8000/docs
```

---

# ▶ Running the Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```
http://localhost:5173
```

---

#  Static Analysis Workflow

```text
Upload Python File
        │
        ▼
Store File
        │
        ▼
Run Pylint
        │
        ▼
Run Bandit
        │
        ▼
Run Radon
        │
        ▼
Save Analysis Report
        │
        ▼
Display Report
```

---

#  Current Progress

##  Day 1

- Requirement Analysis
- FastAPI Project Setup
- Initial API
- Documentation

---

##  Day 2

- PostgreSQL Integration
- SQLAlchemy Models
- JWT Authentication
- User Registration
- User Login

---

##  Day 3

- React Frontend
- Login Page
- Register Page
- Dashboard
- Navigation

---

##  Day 4

- File Upload
- Upload History
- Backend–Frontend Integration

---

##  Day 5

- Pylint Integration
- Code Quality Report
- Interactive Report UI

---

##  Day 6

- Bandit Integration
- Radon Integration
- Combined Static Analysis
- Enhanced Upload Reports

---

##  Day 7

- Save Reports in PostgreSQL
- Report History APIs
- Reports Dashboard
- View Previous Reports
- Improved Report UI

---

##  Day 8

- OpenAI API Configuration
- AI Code Review Service
- AI Review Saved with Reports
- AI Review Display on Upload Page
- AI Review Display in Report History

---

##  Day 9

- AI Review Severity Levels
- Severity Summary Counts
- Critical, High, Medium, Low, and Info Labels
- Severity Findings on Upload Page
- Severity Findings in Report History

---

##  Day 10

- Automatic Documentation Generator
- Function Documentation Extraction
- Class Documentation Extraction
- Documentation Saved with Reports
- Documentation Display on Upload Page
- Documentation Display in Report History

---

##  Day 11

- Review History Search
- Report Filtering
- Report Sorting
- Report Count Summary
- Report Type Badges

---

##  Day 12

- Upload Validation
- Registration Validation
- Safer Filename Handling
- Improved Exception Handling
- Validation Test Cases

---

#  Screenshots

## Dashboard

*(Add screenshot later)*

---

## Upload Page

*(Add screenshot later)*

---

## Reports Page

*(Add screenshot later)*

---

## Login Page

*(Add screenshot later)*

---

## Register Page

*(Add screenshot later)*

---

#  Future Enhancements

- AI Code Suggestions
- Auto Code Fixes
- Review Download (PDF)
- Multi-language Support
- GitHub Repository Integration
- Docker Deployment
- CI/CD Pipeline

---

#  Developer

**Arjun Singh**

AI Code Review Assistant Internship Project

Built using **FastAPI**, **React**, **PostgreSQL**, **Pylint**, **Bandit**, and **Radon**.
