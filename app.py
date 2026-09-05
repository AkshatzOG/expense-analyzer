from flask import Flask, render_template, request, jsonify
from analyzer import analyze_expenses, categorize_description

app = Flask(__name__)

@app.route('/')
def dashboard(): return render_template('dashboard.html', page='dashboard')
@app.route('/transactions')
def transactions(): return render_template('transactions.html', page='transactions')
@app.route('/analytics')
def analytics(): return render_template('analytics.html', page='analytics')
@app.route('/budgets')
def budgets(): return render_template('budgets.html', page='budgets')
@app.route('/insights')
def insights(): return render_template('insights.html', page='insights')
@app.route('/settings')
def settings(): return render_template('settings.html', page='settings')

@app.post('/api/analyze')
def api_analyze():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(analyze_expenses(
            data.get('expenses', []),
            data.get('budgets', {}),
            data.get('startDate'),
            data.get('endDate')
        ))
    except Exception as exc:
        return jsonify({'error': str(exc)}), 400

@app.post('/api/categorize')
def api_categorize():
    data = request.get_json(silent=True) or {}
    return jsonify({'category': categorize_description(str(data.get('description', '')) )})

if __name__ == '__main__':
    app.run(debug=True)
