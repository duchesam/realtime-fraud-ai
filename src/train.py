import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
import joblib

from src.features import FEATURE_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODELS_DIR / "model.joblib"
META_PATH = MODELS_DIR / "model_meta.json"

def make_data(n=60000, seed=7):
    rng = np.random.default_rng(seed)

    amount = rng.lognormal(3.2, 1.0, n)
    is_international = rng.binomial(1, 0.12, n)
    distance_km = np.clip(rng.normal(25, 40, n), 0, 2000)
    device_trust = np.clip(rng.beta(2, 2, n), 0, 1)
    prev_chargeback = rng.binomial(1, 0.05, n)
    merchant_risk = np.clip(rng.beta(2, 5, n), 0, 1)

    # synth "behavior" features (simulate historical patterns)
    user_txn_count_1h = rng.poisson(2.0, n)
    user_amount_sum_1h = user_txn_count_1h * rng.lognormal(3.0, 0.8, n)
    user_unique_merchants_24h = np.clip(rng.poisson(3.0, n), 0, 30)
    merchant_txn_count_1h = rng.poisson(10.0, n)

    # fraud logit with behavior influence
    z = (
        0.7 * np.log1p(amount)
        + 1.1 * is_international
        + 1.0 * merchant_risk
        - 1.2 * device_trust
        + 1.0 * prev_chargeback
        + 0.3 * (distance_km / 500)
        + 0.35 * np.log1p(user_txn_count_1h)
        + 0.25 * np.log1p(user_amount_sum_1h / 100)
        + 0.25 * np.log1p(user_unique_merchants_24h)
        + 0.20 * np.log1p(merchant_txn_count_1h)
    )

    p = 1 / (1 + np.exp(-(z - 3.3)))
    y = rng.binomial(1, p)

    df = pd.DataFrame({
        "amount": amount,
        "is_international": is_international,
        "distance_km": distance_km,
        "device_trust": device_trust,
        "prev_chargeback": prev_chargeback,
        "merchant_risk": merchant_risk,
        "user_txn_count_1h": user_txn_count_1h,
        "user_amount_sum_1h": user_amount_sum_1h,
        "user_unique_merchants_24h": user_unique_merchants_24h,
        "merchant_txn_count_1h": merchant_txn_count_1h,
        "label": y,
    })
    return df

def main():
    df = make_data()
    X = df[FEATURE_COLUMNS]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=3000, class_weight="balanced")),
    ])

    model.fit(X_train, y_train)
    probs = model.predict_proba(X_test)[:, 1]
    ap = average_precision_score(y_test, probs)

    print("Average Precision (PR-AUC):", round(float(ap), 4))

    joblib.dump(model, MODEL_PATH)

    META_PATH.write_text(json.dumps({
        "model_version": "v2",
        "features": FEATURE_COLUMNS
    }, indent=2))

    print("Model saved successfully ✅")

if __name__ == "__main__":
    main()
