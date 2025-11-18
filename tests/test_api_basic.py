import os, sys, json
from fastapi.testclient import TestClient
sys.path.append(str(os.path.dirname(os.path.dirname(__file__))))  # repo root
from api.app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_ingest_missing_auth():
    payload = {'event_id':'e1','timestamp':'2025-01-01T00:00:00Z','tenant_id':'t1','source':'svc','service':'s','environment':'prod','type':'log','payload':{}}
    r = client.post('/v1/events', json=payload)
    assert r.status_code == 401
