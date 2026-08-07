from flask import Flask, render_template, request, redirect, url_for
import re
import os

app = Flask(__name__)

EXPENSES_FILE = "expenses.txt"

# Keywords used to auto-detect a category from the description text.
# (Unit III - Regex)
CATEGORY_KEYWORDS = {
    "Food": ["swiggy", "zomato", "restaurant", "food", "cafe", "pizza",
             "lunch", "dinner", "breakfast", "snacks"],
    "Travel": ["uber", "ola", "petrol", "bus", "train", "travel", "fuel",
               "flight", "cab", "taxi", "airport"],
    "Shopping": ["amazon", "flipkart", "shopping", "mall", "myntra"],
    "Bills": ["bill", "recharge", "electricity", "rent", "wifi",
              "credit card", "emi", "insurance", "subscription"],
    "Entertainment": ["netflix", "movie", "spotify", "prime", "game", "cinema"],
}

# Fixed monthly budget limit per category, used for the budget alert feature.
BUDGET_LIMITS = {
    "Food": 2000,
    "Travel": 1500,
    "Shopping": 2500,
    "Bills": 2000,
    "Entertainment": 1000,
    "Other": 1500,
}


def categorize(description):
    """
    Feature: Expense categorization.
    Scans the description for known keywords using regex and returns
    the matching category. Returns 'Other' if nothing matches.
    """
    text = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for word in keywords:
            if re.search(word, text):
                return category
    return "Other"


def save_expense(amount, description, category):
    """Appends one expense as a comma-separated line to the text file."""
    line = f"{amount},{category},{description}\n"
    with open(EXPENSES_FILE, "a") as file:
        file.write(line)


def read_expenses():
    """
    Reads all expenses from the text file.

    IMPORTANT FIX: each line is parsed inside its OWN try/except.
    In the original version, one bad line (blank line, wrong number
    of commas, etc.) would throw an exception that stopped the whole
    loop early, silently losing every line after it. Here, a bad line
    is skipped and reading continues normally.
    """
    expenses = []

    if not os.path.exists(EXPENSES_FILE):
        return expenses

    with open(EXPENSES_FILE, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            parts = line.split(",", 2)  # split into at most 3 pieces
            if len(parts) != 3:
                continue

            try:
                amount = float(parts[0])
                category = parts[1]
                description = parts[2]
                expenses.append({
                    "amount": amount,
                    "category": category,
                    "description": description,
                })
            except ValueError:
                continue  # skip only this line, keep reading the rest

    return expenses


def get_category_totals(expenses):
    """Feature: Spending insights. Returns {category: total_amount}."""
    totals = {}
    for e in expenses:
        cat = e["category"]
        totals[cat] = totals.get(cat, 0) + e["amount"]
    return totals


def get_budget_alerts(totals):
    """Feature: Budget alerts. Compares each category's spend to its limit."""
    alerts = []
    for category, spent in totals.items():
        limit = BUDGET_LIMITS.get(category, 1500)
        if spent > limit:
            over = spent - limit
            alerts.append(
                f"{category} budget exceeded by Rs.{over:.2f} "
                f"(spent Rs.{spent:.2f} of Rs.{limit})"
            )
    return alerts


def find_duplicates(expenses):
    """
    Feature: Duplicate transaction detection.
    Flags an expense as a likely duplicate if the same amount, category,
    and description already appeared earlier in the list.
    """
    seen = set()
    duplicates = []
    for e in expenses:
        key = (e["amount"], e["category"], e["description"].lower())
        if key in seen:
            duplicates.append(
                f"Possible duplicate: Rs.{e['amount']:.2f} in {e['category']} "
                f"- '{e['description']}'"
            )
        else:
            seen.add(key)
    return duplicates


def get_savings_suggestions(totals, total_spent):
    """Feature: Savings suggestions. Simple rule-based tips."""
    suggestions = []

    if total_spent == 0:
        return ["Add some expenses to get suggestions."]

    for category, amount in totals.items():
        percent = (amount / total_spent) * 100
        if percent > 40:
            suggestions.append(
                f"{category} is {percent:.1f}% of your total spending. "
                f"Try to cut back here."
            )

    if not suggestions:
        suggestions.append("Your spending looks fairly balanced across categories.")

    return suggestions


@app.route("/")
def home():
    """
    Single-page dashboard: the add-expense form, the analysis (insights,
    alerts, suggestions), and the transaction list all live here, so
    nothing is hidden behind a second page you have to remember to visit.
    """
    msg = request.args.get("msg")
    expenses = read_expenses()
    recent = list(reversed(expenses))  # newest first

    totals = get_category_totals(expenses)
    total_spent = sum(totals.values())
    top_category = max(totals, key=totals.get) if totals else None

    budget_alerts = get_budget_alerts(totals)
    duplicate_alerts = find_duplicates(expenses)
    suggestions = get_savings_suggestions(totals, total_spent)

    return render_template(
        "index.html",
        expenses=recent,
        msg=msg,
        totals=totals,
        total_spent=total_spent,
        top_category=top_category,
        budget_alerts=budget_alerts,
        duplicate_alerts=duplicate_alerts,
        suggestions=suggestions,
    )


@app.route("/add", methods=["POST"])
def add():
    try:
        amount = float(request.form["amount"])
        description = request.form["description"].strip()

        if amount <= 0 or not description:
            return redirect(url_for("home", msg="Please enter a valid amount and description"))

        category = categorize(description)
        save_expense(amount, description, category)
        return redirect(url_for("home", msg=f"Added and categorized as '{category}'"))

    except ValueError:
        return redirect(url_for("home", msg="Amount must be a number"))


if __name__ == "__main__":
    app.run(debug=True)
