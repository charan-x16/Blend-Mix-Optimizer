# core/classification.py

def classify_vendor(row):
    """
    Classification logic:
    - Vendor must have non-zero presence to be CORE/FLEX
    """
    if row["max_pct"] == 0:
        return "PENALTY"

    if row["spread_pct"] <= 3:
        return "CORE"
    elif row["spread_pct"] <= 6:
        return "FLEX"
    else:
        return "PENALTY"
