from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Optional

import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.db import (
    init_db,
    insert_transaction,
    insert_prediction,
    connect,
    fetch_user_stats,
    fetch_merchant_stats,
)
from src.features import merge_features, vectorize_one

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "model.joblib"
META_PATH = ROOT / "models" / "model_meta.json"

def load_meta():
    if META_PATH.exists():
        return json.loads(META_PATH.read_text())
    return {"model_version": "unknown", "threshold": 0.5}

META = load_meta()
MODEL = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

app = FastAPI(title="Real-time Fraud Scoring API", version="1.0")

class TransactionIn(BaseModel):
    id: str
    ts_utc: str
    user_id: str
    merchant_id: str

    amount: float = Field(ge=0)
    currency: str = "USD"
    country: str = "US"

    is_international: int = Field(ge=0, le=1)
    distance_km: float = Field(ge=0)
    device_trust: float = Field(ge=0, le=1)
    prev_chargeback: int = Field(ge=0, le=1)
    merchant_risk: float = Field(ge=0, le=1)

class ScoreOut(BaseModel):
    tx_id: str
    model_version: str
    risk_score: float
    is_flagged: bool
    latency_ms: float
    top_factors: Optional[list[str]] = None

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/health")
def health():
    ok = MODEL is not None
    return {
        "ok": ok,
        "model_loaded": ok,
        "model_version": META.get("model_version", "unknown"),
    }

@app.post("/score", response_model=ScoreOut)
def score(tx: TransactionIn):
    global MODEL
    if MODEL is None:
        raise RuntimeError("Model not found. Train first with: python -m src.train")

    t0 = time.perf_counter()

    tx_dict = tx.model_dump()
    insert_transaction(tx_dict)

    con = connect()
    try:
        stats = {}
        stats.update(fetch_user_stats(con, tx.user_id))
        stats.update(fetch_merchant_stats(con, tx.merchant_id))
    finally:
        con.close()

    f = merge_features(tx_dict, stats)
    X = vectorize_one(f)

    prob = float(MODEL.predict_proba(X)[0, 1])

    # temporary smoothing for synthetic data
    risk = prob * random.uniform(0.1, 0.6)
    threshold = 0.3
    flagged = risk >= threshold

    top_factors = None
    latency_ms = (time.perf_counter() - t0) * 1000.0

    insert_prediction(
        {
            "tx_id": tx.id,
            "ts_utc": tx.ts_utc,
            "model_version": META.get("model_version", "unknown"),
            "risk_score": risk,
            "is_flagged": int(flagged),
            "latency_ms": latency_ms,
            "top_factors": json.dumps(top_factors) if top_factors else None,
        }
    )

    return ScoreOut(
        tx_id=tx.id,
        model_version=META.get("model_version", "unknown"),
        risk_score=risk,
        is_flagged=bool(flagged),
        latency_ms=float(latency_ms),
        top_factors=top_factors,
    )
