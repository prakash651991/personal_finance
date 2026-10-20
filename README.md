# Personal Finance App (MVP)

Monorepo with Vercel-ready React frontend, FastAPI backend, and Supabase PostgreSQL.

## Run backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

## Database

Apply `supabase/migrations/0001_initial.sql` to your Supabase project.
Seed categories are inserted by the migration's companion step (see docs).
