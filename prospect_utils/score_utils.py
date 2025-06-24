import numpy as np

def normalize(val, min_val, max_val):
    """Min-max normalization with clipping for safety."""
    return (val - min_val) / (max_val - min_val) if max_val > min_val else 0.0

def rule_based_score(row):
    """
    Rule-based scoring logic for prospect evaluation.
    You can extend this with weights and feature logic as needed.
    """
    score = 0.0

    # AUM weighting
    aum = row.get("AUM", 0)
    score += normalize(aum, 10, 1000) * 0.6  # assume AUM in millions

    # Strategy preference
    strat = str(row.get("Strategy", "")).lower()
    if "alts" in strat or "hedge" in strat:
        score += 0.2
    elif "etf" in strat or "index" in strat:
        score += 0.1

    # Metro bonus if available
    metro = str(row.get("Metro", "")).lower()
    if metro in ["new york", "los angeles", "chicago", "houston", "miami"]:
        score += 0.1

    # Clip final score
    return round(min(score, 1.0), 4)
