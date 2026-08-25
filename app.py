from flask import Flask, render_template, request, redirect

app = Flask(__name__)

FILE = "expenses.txt"

food = ["food", "swiggy", "zomato", "pizza", "restaurant"]
travel = ["uber", "ola", "bus", "train", "petrol"]
shopping = ["amazon", "flipkart", "myntra", "mall", "shopping"]
bills = ["bill", "electricity", "rent", "wifi", "recharge"]
entertainment = ["movie", "netflix", "spotify", "game"]

budget = {
    "Food": 2000,
    "Travel": 1500,
    "Shopping": 2500,
    "Bills": 2000,
    "Entertainment": 1000,
    "Other": 1500
}


def get_category(description):
    description = description.lower()

    for word in food:
        if word in description:
            return "Food"

    for word in travel:
        if word in description:
            return "Travel"

    for word in shopping:
        if word in description:
            return "Shopping"

    for word in bills:
        if word in description:
            return "Bills"

    for word in entertainment:
        if word in description:
            return "Entertainment"

    return "Other"


def read_expenses():
    expenses = []

    try:
        file = open(FILE, "r")

        for line in file:
            data = line.strip().split(",")

            if len(data) == 3:
                expenses.append([
                    float(data[0]),
                    data[1],
                    data[2]
                ])

        file.close()

    except:
        pass

    return expenses


def save_expense(amount, category, description):
    file = open(FILE, "a")
    file.write(str(amount) + "," + category + "," + description + "\n")
    file.close()


def analyze(expenses):
    totals = {}
    total = 0

    for expense in expenses:
        amount = expense[0]
        category = expense[1]

        total = total + amount

        if category in totals:
            totals[category] = totals[category] + amount
        else:
            totals[category] = amount

    top = ""
    top_amount = 0
    alerts = []
    suggestions = []

    for category in totals:

        if totals[category] > top_amount:
            top_amount = totals[category]
            top = category

        if totals[category] > budget[category]:
            extra = totals[category] - budget[category]

            alerts.append(
                category + " budget exceeded by Rs. " + str(extra)
            )

            suggestions.append(
                "Reduce " + category +
                " spending. You can try to save Rs. " +
                str(extra)
            )

    if len(suggestions) == 0:
        suggestions.append(
            "Your spending is within the set budgets."
        )

    return totals, total, top, alerts, suggestions


def find_duplicates(expenses):
    duplicates = []

    for i in range(len(expenses)):
        for j in range(i + 1, len(expenses)):

            if expenses[i] == expenses[j]:
                duplicates.append(expenses[i])

    return duplicates


@app.route("/")
def home():

    expenses = read_expenses()

    totals, total, top, alerts, suggestions = analyze(expenses)

    duplicates = find_duplicates(expenses)

    return render_template(
        "index.html",
        expenses=expenses,
        totals=totals,
        total=total,
        top=top,
        alerts=alerts,
        suggestions=suggestions,
        duplicates=duplicates
    )


@app.route("/add", methods=["POST"])
def add():

    try:
        amount = float(request.form["amount"])
    except:
        return redirect("/")

    description = request.form["description"]

    if amount <= 0 or description == "":
        return redirect("/")

    category = get_category(description)

    save_expense(amount, category, description)

    return redirect("/")


@app.route("/clear", methods=["POST"])
def clear():

    file = open(FILE, "w")
    file.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
