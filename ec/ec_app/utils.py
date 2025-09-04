# ec_app/utils.py
import pandas as pd
import numpy as np
from datetime import datetime

DATE_CANDIDATES = [
    "date", "txn date", "transaction date", "value dt", "value date",
    "posting date", "book date", "txndate", "trans date",
]
NARRATION_CANDIDATES = ["narration", "description", "particulars", "details", "remark"]
WITHDRAW_CANDIDATES = ["withdrawal amt.", "withdrawal amount", "debit", "debit amt", "dr amount", "withdrawal"]
DEPOSIT_CANDIDATES = ["deposit amt.", "deposit amount", "credit", "credit amt", "cr amount", "deposit"]
BALANCE_CANDIDATES = ["closing balance", "balance", "running balance", "avail bal"]

def _first_col(df, candidates):
    cols = {c.lower().strip(): c for c in df.columns}
    for name in candidates:
        if name in cols:
            return cols[name]
    # fallback: fuzzy match
    for c in df.columns:
        lc = c.lower().strip()
        if any(name in lc for name in candidates):
            return c
    return None

def _parse_date_series(s):
    """Handle strings (dd/mm/yy), mixed, and Excel serials."""
    # If numeric → likely Excel serial (or pure int yyyymmdd in some cases)
    if pd.api.types.is_numeric_dtype(s):
        # Excel serial (base 1899-12-30)
        base = pd.Timestamp("1899-12-30")
        dt = base + pd.to_timedelta(s.astype("float"), unit="D")
        return dt.dt.date

    # Strings → try dayfirst with coercion
    # (two-digit years like 31/07/25 will become 2025-07-31)
    dt = pd.to_datetime(s, dayfirst=True, errors="coerce", infer_datetime_format=True)
    return dt.dt.date

def _to_num(s):
    # Convert to float; handle commas/strings; NaN→0.0
    if s is None:
        return pd.Series(dtype=float)
    if s.dtype == object:
        s = s.replace(r"[,\s]", "", regex=True)
    return pd.to_numeric(s, errors="coerce").fillna(0.0)

def normalize_statement(df: pd.DataFrame) -> pd.DataFrame:
    # Lower/strip column names for matching
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    lower_map = {c.lower(): c for c in df.columns}

    date_col = _first_col(df, DATE_CANDIDATES)
    narr_col = _first_col(df, NARRATION_CANDIDATES)
    w_col    = _first_col(df, WITHDRAW_CANDIDATES)
    d_col    = _first_col(df, DEPOSIT_CANDIDATES)
    bal_col  = _first_col(df, BALANCE_CANDIDATES)

    if not date_col or not narr_col:
        raise ValueError("Could not detect date or narration columns in the uploaded file.")

    # Parse date
    parsed_date = _parse_date_series(df[date_col])

    # If some rows failed to parse, try a second pass (strip dots, etc.)
    if parsed_date.isna().any():
        fallback = pd.to_datetime(
            df[date_col].astype(str).str.replace(".", "/", regex=False),
            dayfirst=True, errors="coerce"
        ).dt.date
        parsed_date = parsed_date.fillna(fallback)

    if parsed_date.isna().all():
        raise ValueError("Failed to parse any dates; please check your statement’s date format.")

    # Numbers
    withdrawal = _to_num(df[w_col]) if w_col else pd.Series([0.0]*len(df))
    deposit    = _to_num(df[d_col]) if d_col else pd.Series([0.0]*len(df))
    balance    = _to_num(df[bal_col]) if bal_col else pd.Series([np.nan]*len(df))

    out = pd.DataFrame({
        "date": parsed_date,
        "narration": df[narr_col].astype(str),
        "withdrawal": withdrawal,
        "deposit": deposit,
        "balance": balance,
    })

    # Drop rows that have no money movement and no narration/date
    out = out[~(out["withdrawal"].eq(0) & out["deposit"].eq(0) & out["narration"].str.strip().eq(""))]
    return out.reset_index(drop=True)
