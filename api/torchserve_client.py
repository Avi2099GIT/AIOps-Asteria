import requests, os, json

TORCHSERVE_URL = os.environ.get('TORCHSERVE_URL','http://localhost:8080/predictions/anomaly')

def predict_anomaly(embedding=None, features=None):
    payload = [{
        "body": {
            "embedding": embedding,
            "features": features
        }
    }]
    
    r = requests.post(TORCHSERVE_URL, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()
