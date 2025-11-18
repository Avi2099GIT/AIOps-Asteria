
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.features.client import FeatureClient
from torchserve_client import predict_anomaly as ts_predict

router = APIRouter(tags=["anomaly", "prediction"])

ANOMALY_LOG_PATH = os.environ.get("ASTERIA_ANOMALY_LOG", "/tmp/asteria_anomalies.log")


class AnomalyRequest(BaseModel):
    tenant_id: str
    service: str
    environment: str
    message: str = Field(..., description="Raw log line or message to score")
    tags: Dict[str, Any] = Field(default_factory=dict)


class AnomalyResponse(BaseModel):
    tenant_id: str
    service: str
    environment: str
    anomaly_score: float
    severity: str
    confidence: float
    features_used: Dict[str, float]
    recommended_actions: List[Dict[str, Any]]
    model_version: str = "ml-v1"
    created_at: datetime


class RecentAnomaly(BaseModel):
    tenant_id: str
    service: str
    environment: str
    anomaly_score: float
    severity: str
    created_at: datetime


def text_to_embedding(text: str, dim: int = 384) -> List[float]:
    """Very simple deterministic text embedding.

    This is a lightweight placeholder that turns the text into a fixed-size
    numeric vector. It is **not** meant to be used for real training, but it
    keeps the end-to-end pipeline working and compatible with the TorchServe
    handler (which expects a 384-d embedding).
    """
    vec = [0.0] * dim
    if not text:
        return vec
    for i, ch in enumerate(text.encode("utf-8")):
        vec[i % dim] += float(ch) / 255.0
    return vec


def derive_severity(score: float) -> str:
    if score >= 0.8:
        return "CRITICAL"
    if score >= 0.6:
        return "HIGH"
    if score >= 0.4:
        return "MEDIUM"
    if score >= 0.2:
        return "LOW"
    return "INFO"


def derive_confidence(score: float) -> float:
    # Simple heuristic: confidence is tied to distance from 0.5
    return round(0.5 + abs(score - 0.5), 3)


def append_anomaly_log(entry: Dict[str, Any]) -> None:
    try:
        line = json.dumps(entry, default=str)
        os.makedirs(os.path.dirname(ANOMALY_LOG_PATH), exist_ok=True)
        with open(ANOMALY_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print("[ASTERIA] failed to write anomaly log:", e, flush=True)


@router.post("/predict/anomaly", response_model=AnomalyResponse)
async def predict_anomaly(req: AnomalyRequest):
    """Phase 5: Main anomaly prediction endpoint.

    Flow:
    1. Turn raw text into a 384-dim embedding.
    2. Fetch rolling metrics/features for the given tenant+service.
    3. Call TorchServe (`/predictions/anomaly`) with embedding + features.
    4. Derive severity, confidence & recommended actions.
    5. Persist the anomaly event (Phase 6 integration).
    """
    # 1) Embedding
    emb = text_to_embedding(req.message, dim=384)

    # 2) Features
    fc = FeatureClient(req.tenant_id)
    features_used = fc.get_features([req.service])
    feature_vector = list(features_used.values())

    # 3) Call TorchServe
    try:
        ts_result = ts_predict(embedding=emb, features=feature_vector)
        anomaly_score = float(ts_result.get("anomaly_score", 0.0))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TorchServe error: {e}")

    # 4) Post-process
    severity = derive_severity(anomaly_score)
    confidence = derive_confidence(anomaly_score)
    created_at = datetime.utcnow()

    recommended_actions: List[Dict[str, Any]] = [
        {
            "type": "scale",
            "target": req.service,
            "min_replicas": 2,
            "max_replicas": 5,
            "reason": f"Anomaly score {anomaly_score:.3f} ({severity})"
        },
        {
            "type": "create_ticket",
            "system": "Jira",
            "summary": f"[Asteria] {severity} anomaly in {req.service}",
            "metadata": {
                "tenant_id": req.tenant_id,
                "environment": req.environment,
                "score": anomaly_score,
                "confidence": confidence,
            }
        }
    ]

    response = AnomalyResponse(
        tenant_id=req.tenant_id,
        service=req.service,
        environment=req.environment,
        anomaly_score=anomaly_score,
        severity=severity,
        confidence=confidence,
        features_used=features_used,
        recommended_actions=recommended_actions,
        created_at=created_at,
    )

    # 5) Persist anomaly event (Phase 6)
    append_anomaly_log(response.dict())

    return response


@router.get("/anomalies/recent", response_model=List[RecentAnomaly])
async def list_recent_anomalies(limit: int = 50):
    """Phase 6: Lightweight anomaly history endpoint.

    Reads the last N anomaly lines written to the anomaly log file.
    This is used by dashboards / UI to show recent incidents.
    """
    if not os.path.exists(ANOMALY_LOG_PATH):
        return []

    lines: List[str] = []
    with open(ANOMALY_LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    result: List[RecentAnomaly] = []
    for line in lines[-limit:]:
        try:
            obj = json.loads(line)
            result.append(
                RecentAnomaly(
                    tenant_id=obj.get("tenant_id", "unknown"),
                    service=obj.get("service", "unknown"),
                    environment=obj.get("environment", "unknown"),
                    anomaly_score=float(obj.get("anomaly_score", 0.0)),
                    severity=obj.get("severity", "INFO"),
                    created_at=datetime.fromisoformat(obj.get("created_at")),
                )
            )
        except Exception:
            continue

    # most recent first
    result.sort(key=lambda x: x.created_at, reverse=True)
    return result
