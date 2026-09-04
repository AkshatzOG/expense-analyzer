# Expense Analyzer V4

Professional, local-first finance dashboard built with Flask + vanilla JavaScript.

## Pages
- Dashboard
- Transactions
- Analytics
- Budgets
- Smart Insights
- Settings

## Storage
Transactions are stored in browser localStorage. Flask exposes stateless Python analysis endpoints and does not persist transaction records.

## Run
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Render:
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app`
