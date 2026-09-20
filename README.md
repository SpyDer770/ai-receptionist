# AI Receptionist

An intelligent AI-powered receptionist that understands natural-language
requests and performs real receptionist tasks.

## Goals

- Book, cancel, and look up appointments
- Answer frequently asked questions (FAQs)
- Collect customer information
- Understand natural-language requests using an LLM

## Technology Stack

| Area | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | React, Vite |
| Database | SQLite (initially) |
| AI | LLM API |
| Testing | Pytest, Playwright |
| Version control | Git, GitHub |

## Current Progress

- [x] Day 1: Project setup, FastAPI `/health` endpoint, React page connected to backend
- [ ] Database and appointment models
- [ ] Appointment booking API
- [ ] LLM integration
- [ ] Automated tests

## Project Structure

```
ai-receptionist/
├── backend/    FastAPI application
├── frontend/   React + Vite user interface
├── tests/      Automated tests
└── docs/       Documentation
```

## How to Run the Backend

From the project root (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
uvicorn main:app --reload
```

- API: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health
- Swagger docs: http://127.0.0.1:8000/docs

## How to Run the Frontend

In a second terminal, from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The page should show **Backend Status: Connected**
when the backend is running.

## Environment Variables

Copy `.env.example` to `.env` and fill in the values. Never commit `.env`.