# Agentic AI Personal Finance Management System

Educational full-stack MVP aligned with the supplied Stage-I report.
Stack: React + Vite, FastAPI, SQLAlchemy, MySQL (SQLite quick-demo fallback).

## Features
- User registration/login with JWT
- Income and expense tracking (add/list/delete)
- Rule-based automatic expense categorization
- Monthly budgets and spending thresholds
- Savings goals and contributions
- Agent-style financial insights (observe → analyze → recommend)
- Dashboard, charts, recent transactions and demo seed data

## Run backend
Python 3.10+:
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

Default database is SQLite for easy first run. To use MySQL, create a database:
```sql
CREATE DATABASE finance_db;
```
Then set `DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/finance_db` in backend/.env.

## Run frontend
In a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. Register, then click **Load demo data**.

## Notes
The finance assistant uses transparent rule-based logic and does not make payments or move money. It is an educational demonstration, not professional financial advice or a production banking system. Do not enter real bank passwords/card details. Customize, test, and understand the code before presenting it.
