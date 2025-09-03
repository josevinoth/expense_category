from .models import Transaction
import re

# Simple rules-based example. Can upgrade to ML/LLM later
CATEGORY_KEYWORDS = {
    "groceries": ["supermarket", "grocery", "veg", "mart"],
    "online purchase": ["amazon", "flipkart", "myntra", "ajio"],
    "fuel": ["hpcl", "bharat petroleum", "fuel", "indian oil"],
    "gas": ["gas", "cylinder", "bharat gas"],
    "loan": ["loan", "emi", "hdfc loan"],
    "utilities": ["eb", "electricity", "water", "bill", "broadband"],
    "travel": ["ola", "uber", "irctc", "flight", "bus"],
    "food": ["swiggy", "zomato", "restaurant", "pizza", "hotel"]
}

def categorize_expenses(df, user):
    transactions = []
    for _, row in df.iterrows():
        narration = str(row.get('Narration', '')).lower()
        category = ""
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in narration for kw in keywords):
                category = cat
                break

        transactions.append(Transaction(
            user=user,
            date=row['Date'],
            narration=row['Narration'],
            withdrawal=row.get('Withdrawal Amt.', 0),
            deposit=row.get('Deposit Amt.', 0),
            balance=row.get('Closing Balance', 0),
            predicted_category=category,
        ))
    return transactions
