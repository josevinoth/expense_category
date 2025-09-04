# ec_app/ml_utils.py
import re
import pandas as pd

CATEGORY_KEYWORDS = {
    "groceries": ["supermarket", "grocery", "veg", "mart", "more", "reliance"],
    "online purchase": ["amazon", "flipkart", "myntra", "ajio"],
    "fuel": ["hpcl", "bharat petroleum", "bpetro", "fuel", "indian oil", "ioc"],
    "gas": ["gas", "cylinder", "bharat gas"],
    "loan": ["loan", "emi", "repayment"],
    "utilities": ["eb", "electricity", "water", "bill", "broadband", "jiofiber", "airtel"],
    "travel": ["ola", "uber", "irctc", "flight", "air", "bus", "metro"],
    "food": ["swiggy", "zomato", "restaurant", "pizza", "hotel", "dine"],
}

def categorize_expenses(narration_series: pd.Series):
    out = []
    for text in narration_series.fillna("").astype(str).str.lower():
        cat = ""
        for c, kws in CATEGORY_KEYWORDS.items():
            if any(kw in text for kw in kws):
                cat = c
                break
        out.append(cat)
    return out
