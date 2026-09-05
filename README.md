# Expense Analyzer V5.2

V5.2 is the **Financial Analytics** milestone built on the V5.0 local-first foundation and V5.1 transaction engine.

## Included

### V5.0 Foundation
- IndexedDB working database
- Automatic V4 localStorage migration
- Income + expense transaction model
- Merchant, payment method, notes and recurring fields
- Portable `.eavault` backup / restore
- CSV export
- PWA shell / service worker

### V5.1 Transaction Engine
- Add, edit and delete transactions
- Expense / income types
- Automatic category suggestion
- Merchant field and merchant inference
- Payment methods
- Recurring transaction flag
- Search across description, merchant, category and notes
- Type/category/payment filters
- Sort by date, amount or description
- Duplicate detection

### V5.2 Financial Analytics
- Selectable 7 / 30 / 90 / 365-day periods
- All-time and custom date ranges
- Current period vs previous comparable period
- Daily cash-movement chart: income vs expenses
- Monthly spending comparison
- Spending velocity
- Projected period spend
- Savings rate
- Category mix and category change analysis
- Weekday spending patterns
- Payment-method breakdown
- Merchant concentration
- Repeated-merchant / recurring signals
- Explainable analytics insights

## Architecture

The browser is the source of truth. Transactions are stored in IndexedDB. Flask is stateless and receives the current ledger only when analysis or categorization is requested.

A `.eavault` file is the portable user-controlled backup. It can be kept outside browser storage for recovery.

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open the local Flask address shown in the terminal.
