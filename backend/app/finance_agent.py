from collections import defaultdict
from datetime import date

KEYWORDS = {
    "Food": ["restaurant", "food", "grocery", "cafe", "lunch", "dinner"],
    "Travel": ["uber", "ola", "bus", "train", "petrol", "fuel", "flight"],
    "Shopping": ["amazon", "shopping", "clothes", "mall", "flipkart"],
    "Bills": ["electricity", "water", "internet", "recharge", "bill", "rent"],
    "Education": ["book", "course", "college", "tuition", "exam"],
    "Health": ["medical", "hospital", "pharmacy", "doctor"]
}

def categorize(description):
    text = (description or "").lower()
    for category, words in KEYWORDS.items():
        if any(word in text for word in words):
            return category
    return "Other"

def build_insights(transactions, budgets, goals):
    month = date.today().strftime("%Y-%m")
    spent = defaultdict(float)
    income = expense = 0.0
    for t in transactions:
        if t.txn_date.strftime("%Y-%m") == month:
            if t.kind == "income":
                income += t.amount
            else:
                expense += t.amount
                spent[t.category] += t.amount
    insights = []
    for b in budgets:
        if b.month == month:
            used = spent[b.category]
            ratio = used / b.limit_amount if b.limit_amount else 0
            if ratio >= 1:
                insights.append({"type":"warning","title":b.category+" budget exceeded","message":f"Spent ₹{used:,.0f} against ₹{b.limit_amount:,.0f}. Review optional spending."})
            elif ratio >= .8:
                insights.append({"type":"caution","title":b.category+" budget nearly used","message":f"You have used {ratio:.0%} of this month's budget."})
    if income:
        left = income-expense
        insights.append({"type":"success" if left >= 0 else "warning","title":"Monthly cash-flow check","message":f"Recorded balance is ₹{left:,.0f}. Review spending and savings goals."})
    if not insights:
        insights.append({"type":"info","title":"Finance assistant is ready","message":"Add transactions and budgets to receive personalized observations."})
    for g in goals:
        progress = g.saved_amount/g.target_amount if g.target_amount else 0
        insights.append({"type":"goal","title":"Goal: "+g.title,"message":f"You have reached {progress:.0%} of your ₹{g.target_amount:,.0f} target."})
    return {"summary":{"income":income,"expenses":expense,"balance":income-expense},
            "insights":insights,
            "agent_steps":["Collected this month's transactions","Grouped expenses by category","Checked budget limits and savings goals","Generated suggested next actions"]}
