import time, json, os
from datetime import datetime

# ✅ FIXED IMPORTS
from app.core.config import settings
from app.db import SessionLocal
from app.db.models import Event




EVENT_FILE = os.environ.get("ASTERIA_EVENT_FILE", "/tmp/asteria_events.log")
POLL_INTERVAL = int(os.environ.get("EVENT_CONSUMER_POLL_INTERVAL", "2"))


def process_line(line):
    try:
        obj = json.loads(line)
        session = SessionLocal()
        evt = Event(
            event_id=obj.get("event_id"),
            raw=obj,
            processed=False,
            created_at=datetime.utcnow()
        )
        session.add(evt)
        session.commit()
        session.refresh(evt)
        session.close()

    except Exception as e:
        print("process_line error:", e)


def run():
    print("Event consumer started, tailing", EVENT_FILE)

    # ensure file exists
    open(EVENT_FILE, "a").close()

    with open(EVENT_FILE, "r") as fh:
        fh.seek(0, os.SEEK_END)  # start tailing new lines only

        while True:
            line = fh.readline()
            if not line:
                time.sleep(POLL_INTERVAL)
                continue

            process_line(line.strip())


if __name__ == "__main__":
    run()
