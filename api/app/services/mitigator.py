import os
import time
import json
import requests
from datetime import datetime, timedelta

# ✅ FIXED IMPORTS
from app.core.config import settings
from app.db import SessionLocal
from app.db.models import Anomaly, Mitigation




SLACK_WEBHOOK = os.environ.get("ASTERIA_SLACK_WEBHOOK", "")
POLL_INTERVAL = int(os.environ.get("MITIGATOR_POLL_INTERVAL", "5"))
CONFIDENCE_THRESHOLD = float(os.environ.get("MITIGATOR_CONF_THRESHOLD", "0.8"))


def send_slack(message: str):
    if not SLACK_WEBHOOK:
        print("Slack webhook not configured:", message)
        return
    payload = {"text": message}
    try:
        requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
    except Exception as e:
        print("Slack send error:", e)


def safe_remediate_action(action_payload: dict):
    try:
        webhook = action_payload.get("webhook")
        if webhook:
            requests.post(webhook, json=action_payload.get("body", {}), timeout=5)
            return {"status": "webhook_called"}

        with open("/tmp/asteria_mitigations.log", "a") as f:
            f.write(json.dumps({"time": datetime.utcnow().isoformat(), "action": action_payload}) + "\n")

        return {"status": "logged"}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_loop():
    print("Mitigator started, polling every", POLL_INTERVAL, "seconds")

    while True:
        try:
            session = SessionLocal()
            cutoff = datetime.utcnow() - timedelta(days=7)

            anomalies = session.query(Anomaly).filter(
                Anomaly.confidence >= CONFIDENCE_THRESHOLD,
                Anomaly.status == "open",
                Anomaly.created_at >= cutoff
            ).limit(50).all()

            for a in anomalies:
                action_payload = {
                    "anomaly_id": int(a.id),
                    "service": a.service,
                    "score": float(a.score),
                    "confidence": float(a.confidence),
                    "suggested_action": "restart_service",
                    "webhook": os.environ.get("MITIGATOR_FALLBACK_WEBHOOK")
                }

                m = Mitigation(anomaly_id=a.id, action=action_payload, status="pending", created_at=datetime.utcnow())
                session.add(m)

                a.status = "mitigating"
                session.commit()

                res = safe_remediate_action(action_payload)
                m.result = res
                m.status = "done" if res.get("status") in ("logged", "webhook_called") else "failed"
                m.completed_at = datetime.utcnow()
                session.commit()

                send_slack(f"Mitigation executed for anomaly {a.id} on {a.service}: {res}")

            session.close()

        except Exception as e:
            print("Mitigator loop error:", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run_loop()
