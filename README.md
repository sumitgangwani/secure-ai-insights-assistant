<<<<<<< HEAD
# Secure AI Insights Assistant

A runnable full-stack prototype for the Futures First Quantitative Engineer assignment. It answers business questions using a SQLite database populated from CSV data, PDF retrieval over internal reports, and an optional OpenAI-backed AI layer. Without an API key, it still runs with a deterministic fallback answer generator.

## Architecture

```text
React UI
  ├─ Chat + examples
  ├─ Charts / insights panel
  └─ Tool trace
        │
        ▼
FastAPI backend
  ├─ /api/chat orchestration
  ├─ SQL tool: read-only named analytics queries
  ├─ PDF retriever: TF-IDF chunk search over internal PDFs
  ├─ Security: role scopes, SQL allow-list checks, PII redaction
  └─ AI service: OpenAI if configured, fallback if not
        │
        ├─ SQLite database loaded from generated CSVs
        └─ Internal PDF reports
```

## Features

- Working FastAPI backend and React frontend
- Random demo datasets: `movies.csv`, `viewers.csv`, `watch_activity.csv`, `reviews.csv`, `marketing_spend.csv`, `regional_performance.csv`
- Generated internal PDF reports: executive report, campaign summary, content roadmap, policy guidelines, audience behavior report
- Multi-source answers combining SQL analytics and PDF retrieval
- At least one chart: top titles by views, plus city engagement summary
- Tool trace showing which backend tools were used
- Role-based access through `x-user-role` header
- Read-only SQL validation and blocked destructive keywords
- PII redaction for emails/phone numbers
- Dockerized setup

## Setup: local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# optional: add OPENAI_API_KEY to .env
uvicorn app.main:app --reload --port 8000
```

The backend initializes demo CSVs, SQLite tables, and PDFs automatically on startup.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Setup: Docker

```bash
cp backend/.env.example backend/.env
# optional: edit backend/.env and add OPENAI_API_KEY
docker compose up --build
```

Frontend: `http://localhost:5173`  
Backend docs: `http://localhost:8000/docs`

## Example questions supported

1. Which titles performed best in 2025?
2. Why is Stellar Run trending recently?
3. Compare Dark Orbit vs Last Kingdom.
4. Which city had the strongest engagement last month?
5. What explains weak comedy performance?
6. What recommendations would you give for leadership?

## Security and privacy notes

- The model never receives unrestricted database access.
- The backend exposes tool-style endpoints and a safe named-query library.
- Custom SQL endpoint allows only single-statement `SELECT` queries and blocks destructive keywords.
- Role checks are enforced via `x-user-role`. In production, replace this demo header with real auth/JWT.
- PII-like email and phone strings are redacted before responses.
- Raw viewer-level data is not surfaced in the UI.

## Assumptions and tradeoffs

- The assignment permits random/demo data, so the repository generates synthetic data and PDFs.
- SQLite is used for portability; PostgreSQL would be better for production concurrency and governance.
- TF-IDF retrieval is used to avoid external vector DB requirements. A production system should use embeddings, metadata filters, and access-control-aware retrieval.
- Auth is intentionally lightweight for demo clarity. Production should add SSO, audit logs, row-level policies, secrets management, and encrypted storage.
- OpenAI is optional. With `OPENAI_API_KEY` set, answers are more natural; without it, the fallback still demonstrates the architecture.

## Useful API endpoints

- `GET /api/health`
- `POST /api/chat` with `{ "question": "Which titles performed best in 2025?" }`
- `GET /api/analytics/top-titles`
- `GET /api/analytics/city-engagement`
- `GET /api/documents/search?q=Stellar Run trending`
- `POST /api/sql/read-only` with `{ "sql": "SELECT * FROM movies" }`
=======
# secure-ai-insights-assistant
>>>>>>> 792dd8e6937eccb595b6146d1d30a0986c642762
