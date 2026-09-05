from collections import defaultdict
from datetime import date, datetime, timedelta

KEYWORDS = {
    'Food': ['food','swiggy','zomato','restaurant','pizza','cafe','coffee','blinkit','zepto','instamart','grocery'],
    'Travel': ['uber','ola','bus','train','petrol','fuel','flight','rickshaw','metro','cab'],
    'Shopping': ['amazon','flipkart','myntra','mall','shopping','ajio','meesho','clothes','electronics'],
    'Bills': ['bill','electricity','rent','wifi','recharge','internet','mobile','insurance'],
    'Entertainment': ['movie','netflix','spotify','game','gaming','prime','youtube','concert'],
    'Health': ['hospital','doctor','medicine','pharmacy','health','gym'],
    'Education': ['course','book','college','school','tuition','education']
}
CATEGORIES = list(KEYWORDS) + ['Other']


def categorize_description(description):
    text = str(description).lower()
    for category, words in KEYWORDS.items():
        if any(word in text for word in words):
            return category
    return 'Other'


def infer_merchant(description):
    text = str(description).strip()
    lower = text.lower()
    known = {
        'swiggy': 'Swiggy', 'zomato': 'Zomato', 'uber': 'Uber', 'ola': 'Ola',
        'amazon': 'Amazon', 'flipkart': 'Flipkart', 'myntra': 'Myntra',
        'netflix': 'Netflix', 'spotify': 'Spotify', 'prime': 'Prime',
        'blinkit': 'Blinkit', 'zepto': 'Zepto', 'youtube': 'YouTube'
    }
    for word, merchant in known.items():
        if word in lower:
            return merchant
    return ''


def parse_day(value):
    try:
        return datetime.strptime(str(value), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def clean_expenses(expenses):
    cleaned = []
    for item in expenses or []:
        try:
            amount = float(item.get('amount', 0))
            description = str(item.get('description', '')).strip()
            category = str(item.get('category', '')).strip() or categorize_description(description)
            spent_on = str(item.get('date', '')).strip()
            kind = str(item.get('type', 'expense')).lower()
            if kind not in ('income', 'expense'):
                kind = 'expense'
            merchant = str(item.get('merchant', '')).strip() or infer_merchant(description)
            payment = str(item.get('paymentMethod', '')).strip()
            if amount > 0 and description and spent_on and parse_day(spent_on):
                cleaned.append({
                    'id': str(item.get('id', '')),
                    'amount': amount,
                    'description': description,
                    'category': category if category in CATEGORIES else 'Other',
                    'date': spent_on,
                    'type': kind,
                    'merchant': merchant,
                    'paymentMethod': payment,
                    'notes': str(item.get('notes', '')).strip(),
                    'recurring': bool(item.get('recurring', False)),
                    'createdAt': str(item.get('createdAt', '')),
                    'updatedAt': str(item.get('updatedAt', ''))
                })
        except (TypeError, ValueError):
            pass
    return cleaned


def _date_bounds(items):
    days = [parse_day(x['date']) for x in items if parse_day(x['date'])]
    if not days:
        return date.today(), date.today()
    return min(days), max(days)


def _period_metrics(items, start, end, budgets):
    selected = [x for x in items if start <= parse_day(x['date']) <= end]
    expenses = [x for x in selected if x['type'] == 'expense']
    incomes = [x for x in selected if x['type'] == 'income']
    total = sum(x['amount'] for x in expenses)
    income_total = sum(x['amount'] for x in incomes)
    cats = defaultdict(float)
    daily = defaultdict(float)
    monthly = defaultdict(float)
    weekdays = defaultdict(float)
    payment_methods = defaultdict(float)
    merchants = defaultdict(float)
    for x in expenses:
        d = parse_day(x['date'])
        cats[x['category']] += x['amount']
        daily[x['date']] += x['amount']
        monthly[d.strftime('%Y-%m')] += x['amount']
        weekdays[d.strftime('%A')] += x['amount']
        payment_methods[x['paymentMethod'] or 'Not specified'] += x['amount']
        merchants[x['merchant'] or x['description']] += x['amount']

    days_elapsed = max(1, (end - start).days + 1)
    today = date.today()
    effective_days = min(days_elapsed, max(1, (today - start).days + 1)) if start <= today else days_elapsed
    velocity = total / effective_days if effective_days else 0
    projected = velocity * days_elapsed
    top = max(cats, key=cats.get) if cats else ''
    top_merchant = max(merchants, key=merchants.get) if merchants else ''
    top_payment = max(payment_methods, key=payment_methods.get) if payment_methods else ''
    savings_rate = ((income_total - total) / income_total * 100) if income_total else 0

    budget_status = []
    for category, limit in budgets.items():
        spent = cats.get(category, 0)
        left = limit - spent
        pct = (spent / limit * 100) if limit > 0 else (100 if spent else 0)
        budget_status.append({
            'category': category,
            'budget': round(limit, 2),
            'spent': round(spent, 2),
            'remaining': round(left, 2),
            'percent': round(pct, 1)
        })

    return {
        'start': start.isoformat(), 'end': end.isoformat(),
        'days': days_elapsed, 'effective_days': effective_days,
        'total': round(total, 2), 'income_total': round(income_total, 2),
        'net_total': round(income_total - total, 2),
        'average': round(total / len(expenses), 2) if expenses else 0,
        'expense_count': len(expenses), 'income_count': len(incomes),
        'transaction_count': len(selected), 'savings_rate': round(savings_rate, 1),
        'velocity': round(velocity, 2), 'projected_total': round(projected, 2),
        'top_category': top, 'top_merchant': top_merchant, 'top_payment_method': top_payment,
        'category_totals': {k: round(v, 2) for k, v in cats.items()},
        'daily_totals': dict(sorted(daily.items())),
        'monthly_totals': dict(sorted(monthly.items())),
        'weekday_totals': dict(weekdays),
        'payment_method_totals': {k: round(v, 2) for k, v in payment_methods.items()},
        'merchant_totals': {k: round(v, 2) for k, v in sorted(merchants.items(), key=lambda x: -x[1])[:10]},
        'budget_status': budget_status,
    }


def _previous_period(start, end):
    length = (end - start).days + 1
    prev_end = start - timedelta(days=1)
    return prev_end - timedelta(days=length - 1), prev_end


def _duplicates(items):
    seen = set()
    duplicates = []
    for x in items:
        key = (round(x['amount'], 2), x['description'].lower(), x['category'].lower(), x['date'])
        if key in seen:
            duplicates.append(x)
        else:
            seen.add(key)
    return duplicates


def analyze_expenses(expenses, budgets, start_date=None, end_date=None):
    items = clean_expenses(expenses)
    budgets = {str(k): max(0, float(v)) for k, v in (budgets or {}).items() if str(k).strip()}
    if not budgets:
        budgets = {c: 0 for c in CATEGORIES}

    data_start, data_end = _date_bounds(items)
    start = parse_day(start_date) if start_date else data_start
    end = parse_day(end_date) if end_date else data_end
    if not start:
        start = data_start
    if not end:
        end = data_end
    if start > end:
        start, end = end, start

    current = _period_metrics(items, start, end, budgets)
    prev_start, prev_end = _previous_period(start, end)
    previous = _period_metrics(items, prev_start, prev_end, budgets)

    alerts = []
    insights = []
    for row in current['budget_status']:
        if row['spent'] > row['budget'] and row['budget'] > 0:
            extra = row['spent'] - row['budget']
            alerts.append({'type': 'danger', 'title': f"{row['category']} is over budget", 'message': f"You are Rs. {extra:,.0f} above this category budget."})
            insights.append({'type': 'warning', 'title': f"Reduce {row['category']} spending", 'message': f"Cutting around Rs. {extra:,.0f} here would bring you back within budget."})
        elif row['budget'] > 0 and row['percent'] >= 80:
            alerts.append({'type': 'warning', 'title': f"{row['category']} is nearing its limit", 'message': f"{row['percent']:.0f}% of the category budget has been used."})

    if current['top_category']:
        insights.append({'type': 'info', 'title': f"{current['top_category']} is your biggest category", 'message': f"Rs. {current['category_totals'][current['top_category']]:,.0f} has been spent here in this period."})

    if current['total'] > previous['total'] and previous['total'] > 0:
        change = (current['total'] - previous['total']) / previous['total'] * 100
        if change >= 10:
            insights.append({'type': 'warning', 'title': 'Spending increased', 'message': f"Expense outflow is {change:.0f}% higher than the previous comparable period."})
    elif previous['total'] > current['total'] and current['total'] > 0:
        change = (previous['total'] - current['total']) / previous['total'] * 100
        if change >= 10:
            insights.append({'type': 'positive', 'title': 'Spending improved', 'message': f"Expense outflow is down {change:.0f}% versus the previous comparable period."})

    if current['velocity'] > 0 and current['days'] >= 7:
        insights.append({'type': 'info', 'title': 'Spending velocity', 'message': f"You are averaging Rs. {current['velocity']:,.0f} of expense outflow per active day in this period."})

    largest = max([x for x in items if x['type'] == 'expense' and start <= parse_day(x['date']) <= end], key=lambda x: x['amount'], default=None)
    if largest and largest['amount'] > max(current['average'] * 2, 1000):
        alerts.append({'type': 'warning', 'title': 'Large transaction detected', 'message': f"{largest['description']} was Rs. {largest['amount']:,.0f}, unusually high compared with your average."})

    duplicates = _duplicates([x for x in items if x['type'] == 'expense'])
    period_duplicates = [x for x in duplicates if start <= parse_day(x['date']) <= end]
    if period_duplicates:
        alerts.append({'type': 'danger', 'title': f"{len(period_duplicates)} possible duplicate transaction(s)", 'message': 'Review matching amount, date, description and category before keeping both.'})

    day_names = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    strongest = max(day_names, key=lambda d: current['weekday_totals'].get(d, 0), default='')
    if strongest and current['weekday_totals'].get(strongest, 0) > 0:
        insights.append({'type': 'info', 'title': f'{strongest} is your highest-spend weekday', 'message': f"Your recorded spending on {strongest}s totals Rs. {current['weekday_totals'][strongest]:,.0f}."})

    recurring = [x for x in items if x.get('recurring') and start <= parse_day(x['date']) <= end]
    recurring_total = sum(x['amount'] for x in recurring if x['type'] == 'expense')
    recurring_merchants = defaultdict(list)
    for x in recurring:
        if x['type'] == 'expense':
            recurring_merchants[x['merchant'] or x['description']].append(x['amount'])

    # Detect repeated merchant/description patterns even when recurring was not manually checked.
    repeated = defaultdict(list)
    for x in items:
        if x['type'] == 'expense' and start <= parse_day(x['date']) <= end:
            key = (x['merchant'] or x['description']).lower()
            repeated[key].append(x)
    detected_recurring = []
    for key, rows in repeated.items():
        if len(rows) >= 2:
            amounts = [r['amount'] for r in rows]
            avg_amount = sum(amounts) / len(amounts)
            if avg_amount > 0:
                detected_recurring.append({'name': rows[0]['merchant'] or rows[0]['description'], 'count': len(rows), 'average': round(avg_amount, 2), 'total': round(sum(amounts), 2)})

    category_changes = []
    for category in set(current['category_totals']) | set(previous['category_totals']):
        now = current['category_totals'].get(category, 0)
        before = previous['category_totals'].get(category, 0)
        if before > 0:
            pct = (now - before) / before * 100
        elif now > 0:
            pct = 100
        else:
            pct = 0
        category_changes.append({'category': category, 'current': round(now,2), 'previous': round(before,2), 'change_percent': round(pct,1)})
    category_changes.sort(key=lambda x: x['current'], reverse=True)

    return {
        **current,
        'previous': previous,
        'period_change_percent': round(((current['total'] - previous['total']) / previous['total'] * 100), 1) if previous['total'] else 0,
        'income_change_percent': round(((current['income_total'] - previous['income_total']) / previous['income_total'] * 100), 1) if previous['income_total'] else 0,
        'category_changes': category_changes,
        'recurring_total': round(recurring_total, 2),
        'recurring_count': len(recurring),
        'detected_recurring': detected_recurring,
        'duplicates': period_duplicates,
        'alerts': alerts,
        'insights': insights or [{'type': 'info', 'title': 'Start tracking your money', 'message': 'Add income and expenses to unlock trends, budgets and personalized recommendations.'}],
        # Backward-compatible aliases used by the V4/V5 dashboard.
        'month_total': current['total'],
        'month_income': current['income_total'],
        'month_net': current['net_total'],
        'week_total': current['total'],
        'week_income': current['income_total'],
        'remaining_budget': round(sum(max(x['remaining'], 0) for x in current['budget_status']), 2),
    }
