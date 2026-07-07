from typing import Any, Dict, List
import numpy as np

FEATURE_COLUMNS = [
    "amount",
    "is_international",
    "distance_km",
    "device_trust",
    "prev_chargeback",
    "merchant_risk",
    # behavior / velocity features
    "user_txn_count_1h",
    "user_amount_sum_1h",
    "user_unique_merchants_24h",
    "merchant_txn_count_1h",
]

def base_features(tx: Dict[str, Any]) -> Dict[str, float]:
    return {
        "amount": float(tx["amount"]),
        "is_international": float(tx["is_international"]),
        "distance_km": float(tx["distance_km"]),
        "device_trust": float(tx["device_trust"]),
        "prev_chargeback": float(tx["prev_chargeback"]),
        "merchant_risk": float(tx["merchant_risk"]),
    }

def merge_features(tx: Dict[str, Any], stats: Dict[str, float]) -> Dict[str, float]:
    f = base_features(tx)
    for k in FEATURE_COLUMNS:
        if k not in f:
            f[k] = float(stats.get(k, 0.0))
    return f

def vectorize_one(f: Dict[str, float]) -> np.ndarray:
    return np.array([[f[c] for c in FEATURE_COLUMNS]], dtype=float)
