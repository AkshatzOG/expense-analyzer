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

def categorize_description(description):
    text = str(description).lower()
    for category, words in KEYWORDS.items():
        if any(word in text for word in words): return category
    return 'Other'

def parse_day(value):
    try: return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError: return None

def clean_expenses(expenses):
    cleaned=[]
    for item in expenses:
        try:
            amount=float(item.get('amount',0)); description=str(item.get('description','')).strip()
            category=str(item.get('category','')).strip() or categorize_description(description)
            spent_on=str(item.get('date','')).strip()
            if amount>0 and description and spent_on:
                cleaned.append({'id':str(item.get('id','')),'amount':amount,'description':description,'category':category,'date':spent_on})
        except (TypeError,ValueError): pass
    return cleaned

def analyze_expenses(expenses, budgets):
    expenses=clean_expenses(expenses)
    budgets={str(k):float(v) for k,v in (budgets or {}).items() if str(k).strip()}
    total=sum(x['amount'] for x in expenses); count=len(expenses); average=total/count if count else 0
    today=date.today(); week_start=today-timedelta(days=today.weekday()); month_start=today.replace(day=1)
    week_total=month_total=0; cats=defaultdict(float); daily=defaultdict(float); monthly=defaultdict(float); weekdays=defaultdict(float)
    for x in expenses:
        d=parse_day(x['date'])
        if not d: continue
        cats[x['category']]+=x['amount']; daily[x['date']]+=x['amount']; monthly[d.strftime('%Y-%m')]+=x['amount']; weekdays[d.strftime('%A')]+=x['amount']
        if week_start<=d<=today: week_total+=x['amount']
        if month_start<=d<=today: month_total+=x['amount']
    top=max(cats,key=cats.get) if cats else ''
    budget_status=[]; remaining=0
    for category,limit in budgets.items():
        spent=cats.get(category,0); left=limit-spent; remaining+=max(left,0); pct=(spent/limit*100) if limit>0 else (100 if spent else 0)
        budget_status.append({'category':category,'budget':round(limit,2),'spent':round(spent,2),'remaining':round(left,2),'percent':round(pct,1)})
    duplicates=[]; seen=set()
    for x in expenses:
        key=(round(x['amount'],2),x['description'].lower(),x['category'].lower(),x['date'])
        if key in seen: duplicates.append(x)
        else: seen.add(key)
    alerts=[]; insights=[]
    for row in budget_status:
        if row['spent']>row['budget']:
            extra=row['spent']-row['budget']; alerts.append({'type':'danger','title':f"{row['category']} is over budget",'message':f"You are Rs. {extra:,.0f} above this category budget."}); insights.append({'type':'warning','title':f"Reduce {row['category']} spending",'message':f"Cutting around Rs. {extra:,.0f} here would bring you back within budget."})
        elif row['budget']>0 and row['percent']>=80:
            alerts.append({'type':'warning','title':f"{row['category']} is nearing its limit",'message':f"{row['percent']:.0f}% of the category budget has been used."})
    if top: insights.append({'type':'info','title':f'{top} is your biggest category','message':f"Rs. {cats[top]:,.0f} has been spent here."})
    largest=max(expenses,key=lambda x:x['amount'],default=None)
    if largest and largest['amount']>max(average*2,1000): insights.append({'type':'warning','title':'Large transaction detected','message':f"{largest['description']} was Rs. {largest['amount']:,.0f}, unusually high compared with your average."})
    if duplicates: alerts.append({'type':'danger','title':f'{len(duplicates)} possible duplicate transaction(s)','message':'Review matching amount, date, description and category before keeping both.'})
    if not expenses: insights.append({'type':'info','title':'Start tracking your spending','message':'Add a few transactions to unlock personalized trends, budgets and recommendations.'})
    day_names=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']; strongest=max(day_names,key=lambda d:weekdays.get(d,0),default='')
    if strongest and weekdays.get(strongest,0)>0: insights.append({'type':'info','title':f'{strongest} is your highest-spend weekday','message':f"Your recorded spending on {strongest}s totals Rs. {weekdays[strongest]:,.0f}."})
    return {'total':round(total,2),'week_total':round(week_total,2),'month_total':round(month_total,2),'average':round(average,2),'transaction_count':count,'top_category':top,'remaining_budget':round(remaining,2),'category_totals':{k:round(v,2) for k,v in cats.items()},'daily_totals':dict(sorted(daily.items())),'monthly_totals':dict(sorted(monthly.items())),'weekday_totals':dict(weekdays),'budget_status':budget_status,'duplicates':duplicates,'alerts':alerts,'insights':insights}
