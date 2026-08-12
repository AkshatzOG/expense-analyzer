from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

FILE_NAME = "expenses.txt"

# lists of keywords for each category, used to guess the category
food_words = ["swiggy", "zomato", "food", "restaurant", "pizza", "lunch", "dinner", "cafe"]
travel_words = ["uber", "ola", "bus", "train", "flight", "taxi", "petrol", "cab"]
shopping_words = ["amazon", "flipkart", "shopping", "mall", "myntra"]
bill_words = ["bill", "recharge", "electricity", "rent", "wifi", "emi", "credit card"]
entertainment_words = ["netflix", "movie", "spotify", "game", "cinema"]

# budget limit for each category, used to show alert if crossed
budget_limits = {
    "Food": 2000,
    "Travel": 1500,
    "Shopping": 2500,
    "Bills": 2000,
    "Entertainment": 1000,
    "Other": 1500
}


# guesses category by checking if any keyword is present in the description
def find_category(desc):
    desc = desc.lower()

    for word in food_words:
        if word in desc:
            return "Food"

    for word in travel_words:
        if word in desc:
            return "Travel"

    for word in shopping_words:
        if word in desc:
            return "Shopping"

    for word in bill_words:
        if word in desc:
            return "Bills"

    for word in entertainment_words:
        if word in desc:
            return "Entertainment"

    return "Other"


# adds one line to the text file
def add_expense_to_file(amount, category, desc):
    file = open(FILE_NAME, "a")
    file.write(str(amount) + "," + category + "," + desc + "\n")
    file.close()


# reads the file and returns a list of expenses
# each expense is stored as [amount, category, description]
def get_all_expenses():
    expenses = []

    if os.path.exists(FILE_NAME) == False:
        return expenses

    file = open(FILE_NAME, "r")
    for line in file:
        line = line.strip()
        if line == "":
            continue

        parts = line.split(",", 2)
        if len(parts) != 3:
            continue

        try:
            amount = float(parts[0])
        except:
            continue

        category = parts[1]
        desc = parts[2]
        expenses.append([amount, category, desc])

    file.close()
    return expenses


# adds up total spent in each category
def get_category_totals(expenses):
    totals = {}
    for e in expenses:
        category = e[1]
        amount = e[0]
        if category in totals:
            totals[category] = totals[category] + amount
        else:
            totals[category] = amount
    return totals


def get_total_spent(totals):
    total = 0
    for category in totals:
        total = total + totals[category]
    return total


# finds category with the highest spending
def get_top_category(totals):
    top_category = None
    top_amount = 0
    for category in totals:
        if totals[category] > top_amount:
            top_amount = totals[category]
            top_category = category
    return top_category


# checks each category against its budget limit
def check_budget(totals):
    alerts = []
    for category in totals:
        spent = totals[category]
        if category in budget_limits:
            limit = budget_limits[category]
        else:
            limit = 1500

        if spent > limit:
            extra = spent - limit
            message = category + " budget exceeded! Spent Rs." + str(spent) + " out of Rs." + str(limit) + " (over by Rs." + str(extra) + ")"
            alerts.append(message)
    return alerts


# compares every expense with every other expense using nested loops
# to find possible duplicate transactions
def check_duplicates(expenses):
    duplicates = []
    n = len(expenses)

    for i in range(n):
        for j in range(i + 1, n):
            amount1 = expenses[i][0]
            category1 = expenses[i][1]
            desc1 = expenses[i][2].lower()

            amount2 = expenses[j][0]
            category2 = expenses[j][1]
            desc2 = expenses[j][2].lower()

            if amount1 == amount2 and category1 == category2 and desc1 == desc2:
                message = "Possible duplicate: Rs." + str(amount1) + " in " + category1 + " - " + expenses[i][2]
                if message not in duplicates:
                    duplicates.append(message)

    return duplicates


# gives simple tips based on which category has high spending
def get_suggestions(totals, total_spent):
    tips = []

    if total_spent == 0:
        tips.append("Add some expenses to get suggestions.")
        return tips

    for category in totals:
        percent = (totals[category] / total_spent) * 100
        if percent > 40:
            tips.append(category + " is " + str(round(percent, 1)) + "% of your total spending. Try to cut back here.")

    if len(tips) == 0:
        tips.append("Your spending looks balanced across categories.")

    return tips


@app.route("/")
def home():
    msg = request.args.get("msg")
    expenses = get_all_expenses()
    recent_expenses = list(reversed(expenses))

    totals = get_category_totals(expenses)
    total_spent = get_total_spent(totals)
    top_category = get_top_category(totals)

    budget_alerts = check_budget(totals)
    duplicate_alerts = check_duplicates(expenses)
    suggestions = get_suggestions(totals, total_spent)

    return render_template(
        "index.html",
        expenses=recent_expenses,
        msg=msg,
        totals=totals,
        total_spent=total_spent,
        top_category=top_category,
        budget_alerts=budget_alerts,
        duplicate_alerts=duplicate_alerts,
        suggestions=suggestions
    )


@app.route("/add", methods=["POST"])
def add():
    amount = request.form["amount"]
    desc = request.form["description"]
    desc = desc.strip()

    try:
        amount = float(amount)
    except:
        return redirect(url_for("home", msg="Amount must be a number"))

    if amount <= 0 or desc == "":
        return redirect(url_for("home", msg="Please enter a valid amount and description"))

    category = find_category(desc)
    add_expense_to_file(amount, category, desc)

    return redirect(url_for("home", msg="Added and categorized as " + category))


@app.route("/clear", methods=["POST"])
def clear():
    file = open(FILE_NAME, "w")
    file.write("")
    file.close()
    return redirect(url_for("home", msg="All data cleared"))


if __name__ == "__main__":
    app.run(debug=True)
