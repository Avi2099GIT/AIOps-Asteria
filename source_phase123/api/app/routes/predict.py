from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
import json

from core.feature_store import FeatureClient
from ml.models.embedding_model import LogEmbeddingModel


router = APIRouter()

# ------------------------------
#   BASELINE PREDICT (Phase 3)
# ------------------------------

class PredictRequest(BaseModel):
    tenant_id: str
    window_start: str
    window_end: str
    services: List[str]
    context: Dict[str, Any] = {}

@router.post("/v1/predict")
async def predict(req: PredictRequest):
    tenant = req.tenant_id
    service = req.services[0]   # only first service supported in scaffold

    fc = FeatureClient(tenant)
    feats = fc.get_features(service)

    response = {
        "incident_probability": round(min(0.95, 0.1 + feats.get("error_rate_5m", 0) * 0.8), 2),
        "predicted_ttf_minutes": 30,
        "top_contributors": [
            {"feature": "error_rate_5m", "score": feats.get("error_rate_5m", 0)}
        ],
        "rca_candidates": [{"service": service, "confidence": 0.6}],
        "recommended_actions": [{"type": "scale", "target": service, "replicas": 2}],
        "model_version": "v0-scaffold-features"
    }
    return response


# ------------------------------
#       ML PREDICT (Phase 4)
# ------------------------------

TORCHSERVE_URL = "http://localhost:8085/predictions/anomaly"

@router.post("/v1/predict-ml")
def predict_ml(request: dict):
    message = request.get("log", "")
    service = request.get("service", "unknown")
    tenant = request.get("tenant_id")

    # 1) Generate log embedding
    emb = LogEmbeddingModel.embed(message)

    # 2) Fetch rolling features
    fc = FeatureClient(tenant)
    feats = fc.get_features(service)

    feature_vector = list(feats.values())

    # 3) Ask TorchServe for anomaly score
    payload = {
        "embedding": emb,
        "features": feature_vector
    }

    resp = requests.post(TORCHSERVE_URL, data=json.dumps(payload))
    result = resp.json()
    anomaly_score = result["anomaly_score"]

    return {
        "anomaly_score": anomaly_score,
        "embedding_norm": float(sum([e * e for e in emb]) ** 0.5),
        "features_used": feats,
        "service": service,
        "model_version": "ml-v1",
        "recommended_actions": [
            {"type": "scale", "target": service, "replicas": 2}
        ]
    }
