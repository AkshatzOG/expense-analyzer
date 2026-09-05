# Expense Analyzer V5

V5 upgrades the V4 local-first dashboard into a personal finance intelligence foundation.

## V5 foundation
- IndexedDB working database
- Automatic V4 localStorage migration
- Income + expense transactions
- Merchant, payment method, notes and recurring flags
- Net cash flow + savings rate
- Advanced transaction ledger
- Portable `.eavault` backup/restore
- CSV export
- Explainable insights and budget alerts
- PWA shell/service worker

## Run
```bash
pip install -r requirements.txt
python app.py
```
Then open the local Flask address.

The Flask backend is intentionally stateless for transaction data. The browser database is the source of truth.
