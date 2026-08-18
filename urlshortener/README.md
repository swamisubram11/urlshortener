# URL Shortener — AI-Assisted Engineering Assignment

A runnable FastAPI URL shortener with custom aliases, expiry handling, redirect analytics, tests, and a documented engineer-led AI-assisted workflow.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.

## Quality checks

```bash
pytest -q
ruff check .
```

See `docs/ENGINEERING_REPORT.md` for design rationale, task decomposition, AI traceability, validation, risks, and the three requested scenarios.
