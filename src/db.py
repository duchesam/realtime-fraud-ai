import sqlite3
from pathlib import Path
from typing import Any, Dict

DB_PATH = Path(__file__).resolve().parents[1] / "realtime.db"

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS transactions (
  id TEXT PRIMARY KEY,
  ts_utc TEXT NOT NULL,
  user_id TEXT NOT NULL,
  merchant_id TEXT NOT NULL,
  amount REAL NOT NULL,
  currency TEXT NOT NULL,
  country TEXT NOT NULL,
  is_international INTEGER NOT NULL,
  distance_km REAL NOT NULL,
  device_trust REAL NOT NULL,
  prev_chargeback INTEGER NOT NULL,
  merchant_risk REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS predictions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tx_id TEXT NOT NULL,
  ts_utc TEXT NOT NULL,
  model_version TEXT NOT NULL,
  risk_score REAL NOT NULL,
  is_flagged INTEGER NOT NULL,
  latency_ms REAL NOT NULL,
  top_factors TEXT,
  FOREIGN KEY(tx_id) REFERENCES transactions(id)
);

CREATE INDEX IF NOT EXISTS idx_predictions_ts ON predictions(ts_utc);
CREATE INDEX IF NOT EXISTS idx_predictions_flag ON predictions(is_flagged);
"""

def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db() -> None:
    con = connect()
    try:
        con.executescript(SCHEMA)
        con.commit()
    finally:
        con.close()

def insert_transaction(tx: Dict[str, Any]) -> None:
    con = connect()
    try:
        con.execute(
            """
            INSERT OR REPLACE INTO transactions
            (id, ts_utc, user_id, merchant_id, amount, currency, country,
             is_international, distance_km, device_trust, prev_chargeback,
             merchant_risk)
            VALUES
            (:id, :ts_utc, :user_id, :merchant_id, :amount, :currency, :country,
             :is_international, :distance_km, :device_trust, :prev_chargeback,
             :merchant_risk)
            """,
            tx,
        )
        con.commit()
    finally:
        con.close()

def insert_prediction(pred: Dict[str, Any]) -> None:
    con = connect()
    try:
        con.execute(
            """
            INSERT INTO predictions
            (tx_id, ts_utc, model_version, risk_score, is_flagged, latency_ms, top_factors)
            VALUES
            (:tx_id, :ts_utc, :model_version, :risk_score, :is_flagged, :latency_ms, :top_factors)
            """,
            pred,
        )
        con.commit()
    finally:
        con.close()

def fetch_user_stats(con: sqlite3.Connection, user_id: str) -> dict:
    # last 1 hour stats
    q1 = """
    SELECT
      COUNT(*) as cnt_1h,
      COALESCE(SUM(amount),0) as sum_1h
    FROM transactions
    WHERE user_id = ?
      AND ts_utc >= datetime('now','-1 hour')
    """
    row1 = con.execute(q1, (user_id,)).fetchone()

    # last 24 hours unique merchants
    q2 = """
    SELECT
      COUNT(DISTINCT merchant_id) as uniq_merchants_24h
    FROM transactions
    WHERE user_id = ?
      AND ts_utc >= datetime('now','-24 hour')
    """
    row2 = con.execute(q2, (user_id,)).fetchone()

    return {
        "user_txn_count_1h": float(row1["cnt_1h"] or 0),
        "user_amount_sum_1h": float(row1["sum_1h"] or 0.0),
        "user_unique_merchants_24h": float(row2["uniq_merchants_24h"] or 0),
    }

def fetch_merchant_stats(con: sqlite3.Connection, merchant_id: str) -> dict:
    q = """
    SELECT
      COUNT(*) as m_cnt_1h
    FROM transactions
    WHERE merchant_id = ?
      AND ts_utc >= datetime('now','-1 hour')
    """
    row = con.execute(q, (merchant_id,)).fetchone()
    return {
        "merchant_txn_count_1h": float(row["m_cnt_1h"] or 0),
    }
