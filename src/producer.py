from __future__ import annotations

import asyncio
import random
import uuid
from datetime import datetime, timezone

import requests

API_URL = "http://127.0.0.1:8000/score"

USERS = [f"u{i:04d}" for i in range(1, 501)]
MERCHANTS = [f"m{i:04d}" for i in range(1, 201)]
COUNTRIES = ["US", "US", "US", "CA", "GB", "FR", "DE", "AE", "NG", "BR"]

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def make_tx() -> dict:
    user_id = random.choice(USERS)
    merchant_id = random.choice(MERCHANTS)

    if random.random() < 0.03:
        amount = random.uniform(800, 5000)
    else:
        amount = random.lognormvariate(3.1, 0.9)

    country = random.choice(COUNTRIES)
    is_international = 0 if country == "US" else 1

    distance_km = max(0.0, random.gauss(25, 45))
    if random.random() < 0.05:
        distance_km = random.uniform(300, 2000)

    device_trust = min(1.0, max(0.0, random.betavariate(2, 2)))
    if random.random() < 0.06:
        device_trust = min(1.0, max(0.0, random.betavariate(1, 5)))

    prev_chargeback = 1 if random.random() < 0.04 else 0
    merchant_risk = min(1.0, max(0.0, random.betavariate(2, 5)))
    if random.random() < 0.05:
        merchant_risk = min(1.0, max(0.0, random.betavariate(5, 2)))

    return {
        "id": str(uuid.uuid4()),
        "ts_utc": now_utc_iso(),
        "user_id": user_id,
        "merchant_id": merchant_id,
        "amount": float(amount),
        "currency": "USD",
        "country": country,
        "is_international": int(is_international),
        "distance_km": float(distance_km),
        "device_trust": float(device_trust),
        "prev_chargeback": int(prev_chargeback),
        "merchant_risk": float(merchant_risk),
    }

async def main(rate_per_sec: float = 6.0):
    delay = 1.0 / rate_per_sec

    while True:
        tx = make_tx()
        try:
            r = requests.post(API_URL, json=tx, timeout=2.5)
            if r.status_code == 200:
                out = r.json()
                flag = "🚨" if out["is_flagged"] else "✅"
                print(f"{flag} score={out['risk_score']:.3f} latency={out['latency_ms']:.1f}ms tx={out['tx_id'][:8]}")
            else:
                print("API error:", r.status_code, r.text[:120])
        except Exception as e:
            print("Request failed:", str(e))

        await asyncio.sleep(delay)

if __name__ == "__main__":
    asyncio.run(main())
