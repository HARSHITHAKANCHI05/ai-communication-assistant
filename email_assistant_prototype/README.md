
# AI-Powered Communication Assistant - Prototype (FastAPI + Worker)

This is a small runnable prototype that demonstrates:
- Fetching emails (mock mode, CSV-based)
- Filtering emails (subject/body regex)
- Extracting simple contact info (regex)
- Sentiment (simple heuristic or OpenAI if API key provided)
- Priority scoring (rule-based)
- Generating draft replies (simple template or OpenAI if API key provided)
- Storing emails and processed metadata in SQLite
- A FastAPI backend with endpoints to view emails and trigger mock-fetch
- A worker script to process unprocessed emails

## Quick start (mock mode)

Requirements:
- Python 3.10+
- (Optional) OpenAI Python package & API key if you want LLM replies

1. Create virtual env and install:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Initialize DB (creates `data/emails.db`):
```bash
python db_init.py
```

3. Load sample emails (mock):
```bash
python -m backend.fetch_mock     # loads sample_emails.csv into DB
```

4. Start the API server:
```bash
uvicorn backend.app:app --reload --port 8000
```

5. Run the worker to process unprocessed emails (this applies filters, sentiment, priority, drafts):
```bash
python worker.py
```

6. Explore endpoints:
- `GET http://localhost:8000/emails` - list emails
- `GET http://localhost:8000/emails/{id}` - get email details
- `POST http://localhost:8000/emails/{id}/send` - mark as sent (simulates sending)

## Using OpenAI (optional)

If you set `OPENAI_API_KEY` in the environment, the prototype will attempt to call OpenAI for sentiment classification and draft generation. If not present, it will fallback to simple heuristics and templates.

Set env var (example):
```bash
export OPENAI_API_KEY="sk-..."
```

## Project structure
- `backend/` - FastAPI app + helper to fetch mock emails
- `worker.py` - processor that runs extraction, sentiment, priority, draft generation
- `db_init.py` - creates SQLite DB and tables
- `sample_emails.csv` - seed CSV file with sample support emails
- `requirements.txt` - Python deps

This is a prototype for demonstration and learning. For production usage, use OAuth for email connectors, secure token storage, production DB, queues, vector DB for RAG, robust LLM prompt engineering, and testing.
