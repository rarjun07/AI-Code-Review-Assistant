# AI Code Review Assistant

AI Code Review Assistant is an AI-powered full-stack web application that helps developers and students review source code automatically.

The application analyzes uploaded code using static analysis tools and AI to identify bugs, security issues, code smells, complexity, and improvement suggestions.

## Project Objective

The main objective of this project is to build a production-ready code review assistant using modern full-stack development practices.

## Core Features

- User registration and login
- Upload source code files
- Paste code snippets
- Static code analysis
- AI-powered code review
- Security issue detection
- Complexity analysis
- Review history dashboard
- Report generation

## Tech Stack

### Backend
- FastAPI
- Python
- SQLAlchemy
- PostgreSQL
- JWT Authentication

### Frontend
- React.js
- JavaScript (ES6+)
- CSS
- HTML
  
### Code Analysis
- Pylint
- Bandit
- Radon

### AI Integration
- OpenAI API or any LLM provider

## Current Status

Day 1 completed:
- Requirement analysis
- Initial project structure
- FastAPI backend setup
- Basic API endpoints
- Project documentation started

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API welcome route |
| GET | `/health` | API health check |

## Run Backend Locally

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
