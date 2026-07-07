import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).resolve().parents[1] / "realtime.db"

st.set_page_config(layout="wide")
st.title("🚨 Real-Time Fraud Monitoring")

def load_data():
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT * FROM predictions ORDER BY ts_utc DESC LIMIT 5000",
        con
    )
    con.close()
    return df

df = load_data()

if df.empty:
    st.warning("No data yet. Start producer.")
    st.stop()

df["latency_ms"] = df["latency_ms"].astype(float)
df["risk_score"] = df["risk_score"].astype(float)
df["is_flagged"] = df["is_flagged"].astype(int)

col1, col2, col3 = st.columns(3)

col1.metric("Total Predictions", len(df))
col2.metric("Fraud Rate (%)", round(df["is_flagged"].mean() * 100, 2))
col3.metric("Avg Latency (ms)", round(df["latency_ms"].mean(), 2))

st.subheader("Latency Distribution")
st.line_chart(df["latency_ms"])

st.subheader("Score Distribution")
st.bar_chart(df["risk_score"].value_counts(bins=20).sort_index())

st.subheader("Fraud Over Time")
df_time = df.copy()
df_time["ts_utc"] = pd.to_datetime(df_time["ts_utc"])
df_time = df_time.set_index("ts_utc")
fraud_over_time = df_time["is_flagged"].resample("10s").mean()
st.line_chart(fraud_over_time)

baseline_mean = 0.5
current_mean = df["risk_score"].mean()
drift_score = abs(current_mean - baseline_mean)

st.subheader("Drift Indicator")
st.metric("Score Drift vs Baseline", round(drift_score, 4))
