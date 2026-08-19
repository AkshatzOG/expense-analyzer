# Expense Analyzer

A simple Flask web app that analyzes your spending instead of just storing it.
Built for a BSc-IT Python semester project.

**Live demo:** https://luffycodes.pythonanywhere.com/

## Domain
Finance

## Problem Statement
Most expense trackers just store transactions and leave you to make sense of them.
This project analyzes the data as it comes in and surfaces useful information —
automatic categorization, spending breakdowns, budget warnings, duplicate
detection, and savings tips — without any manual work from the user beyond
entering an amount and a description.

## Core Features
- **Expense categorization** — the description you type is scanned for
  keywords and automatically sorted into a category (Food, Travel, Shopping,
  Bills, Entertainment, or Other)
- **Spending insights** — total spent, category-wise totals, and the
  top spending category, shown on the same page as the form
- **Budget alerts** — each category has a fixed monthly limit; going over
  it triggers a visible warning
- **Duplicate transaction detection** — flags entries with the same
  amount, category, and description as possible duplicates
- **Savings suggestions** — simple tips based on which category is taking
  up a large share of total spending
- **Clear all data** — resets everything back to empty, with a confirmation
  prompt so it can't happen by accident

## Tech Stack
- **Python (Flask)** — all the logic: categorization, totals, alerts,
  duplicate checks, suggestions
- **HTML + Jinja templates** — a single dashboard page, no JavaScript
- **Plain text file (`expenses.txt`)** — stores each expense as one line
  (`amount,category,description`); no database involved

## Project Structure
```
expense-analyzer/
├── app.py              # Flask app and all analysis logic
├── expenses.txt         # stores the data, created/updated at runtime
├── requirements.txt
├── templates/
│   └── index.html       # single dashboard page
└── static/
    └── style.css
```

## How Categorization Works
Each category has a list of keywords. When an expense is added, its
description is checked (lowercased) against each list in turn — the first
match decides the category. If nothing matches, it falls under "Other".

## How Duplicate Detection Works
Every new expense is compared against every existing one using a nested
loop. If the amount, category, and description (case-insensitive) all
match, it's flagged as a possible duplicate.

## How to Run Locally
1. Install Flask:
   ```
   pip install -r requirements.txt
   ```
2. Run the app:
   ```
   python app.py
   ```
3. Open `http://127.0.0.1:5000` in your browser.

## Deployment
Hosted on PythonAnywhere's free tier, which runs Flask apps as a persistent
process with real file storage — so `expenses.txt` isn't wiped between
visits the way it would be on a serverless or auto-sleeping host.

## Notes
No database or external service is used on purpose. A plain text file is
enough for this project's scope, and it keeps the whole thing dependency-free
and easy to explain.