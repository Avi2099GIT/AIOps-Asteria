import os, sys, json, types
from fastapi.testclient import TestClient
sys.path.append(str(os.path.dirname(os.path.dirname(__file__))))  # repo root

# monkeypatch api.torchserve_client.predict_anomaly
import api.torchserve_client as ts_client
def mock_predict(embedding=None, features=None):
    # deterministic pseudo-score for tests
    s = sum((embedding or [0])) % 100 / 100.0
    return {'anomaly_score': s}

ts_client.predict_anomaly = mock_predict

from api.app.main import app
client = TestClient(app)

def test_predict_anomaly():
    payload = {'tenant_id':'demo-tenant','service':'checkout','environment':'prod','message':'timeout error'}
    r = client.post('/v1/predict/anomaly', json=payload)
    assert r.status_code == 200
    body = r.json()
    assert 'anomaly_score' in body
    assert 'severity' in body
