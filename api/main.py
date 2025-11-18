
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid


from torchserve_client import predict_anomaly

app = FastAPI(
    title="Asteria AIOps API",
    version="0.2.0",
    description="Unified API layer for log ingestion, anomaly detection, and incident management."
)

class LogRecord(BaseModel):
    id: Optional[str] = None
    timestamp: datetime
    service: str
    level: str
    message: str
    embedding: Optional[list[float]] = None
    features: Optional[list[float]] = None

class AnomalyResult(BaseModel):
    id: str
    log_id: Optional[str] = None
    timestamp: datetime
    service: str
    anomaly_score: float
    severity: str
    confidence: float
    raw_response: dict

class Incident(BaseModel):
    id: str
    created_at: datetime
    service: str
    summary: str
    details: Optional[str] = None
    severity: str
    status: str = "open"
    anomaly_ids: List[str] = []

class IncidentCreate(BaseModel):
    service: str
    summary: str
    details: Optional[str] = None
    severity: str = "medium"
    anomaly_ids: List[str] = []

LOG_STORE: list[LogRecord] = []
ANOMALY_STORE: list[AnomalyResult] = []
INCIDENT_STORE: list[Incident] = []

@app.get("/health")
def health():
    return {"status": "ok", "logs": len(LOG_STORE), "anomalies": len(ANOMALY_STORE), "incidents": len(INCIDENT_STORE)}

@app.post("/logs/ingest", response_model=LogRecord)
def ingest_log(log: LogRecord):
    if log.id is None:
        log.id = str(uuid.uuid4())
    LOG_STORE.append(log)
    return log

@app.get("/logs", response_model=List[LogRecord])
def list_logs(service: Optional[str] = None, level: Optional[str] = None):
    results = LOG_STORE
    if service:
        results = [l for l in results if l.service == service]
    if level:
        results = [l for l in results if l.level.lower() == level.lower()]
    return results

@app.post("/anomalies/detect", response_model=List[AnomalyResult])
def detect_anomalies_for_logs(log_ids: Optional[List[str]] = None):
    # If log_ids is provided -> run anomaly detection only for those logs.
    # If omitted -> run for all logs in LOG_STORE.
    target_logs = LOG_STORE
    if log_ids:
        id_set = set(log_ids)
        target_logs = [l for l in LOG_STORE if l.id in id_set]

    results: list[AnomalyResult] = []
    for l in target_logs:
        try:
            resp = predict_anomaly(embedding=l.embedding, features=l.features)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"TorchServe error: {e}")

        anomaly = AnomalyResult(
            id=str(uuid.uuid4()),
            log_id=l.id,
            timestamp=l.timestamp,
            service=l.service,
            anomaly_score=float(resp.get("anomaly_score", 0.0)),
            severity=str(resp.get("severity", "unknown")),
            confidence=float(resp.get("confidence", 0.0)),
            raw_response=resp,
        )
        ANOMALY_STORE.append(anomaly)
        results.append(anomaly)

    return results

@app.get("/anomalies", response_model=List[AnomalyResult])
def list_anomalies(service: Optional[str] = None, min_score: Optional[float] = None):
    results = ANOMALY_STORE
    if service:
        results = [a for a in results if a.service == service]
    if min_score is not None:
        results = [a for a in results if a.anomaly_score >= min_score]
    return results

@app.post("/incidents", response_model=Incident)
def create_incident(payload: IncidentCreate):
    inc = Incident(
        id=str(uuid.uuid4()),
        created_at=datetime.utcnow(),
        service=payload.service,
        summary=payload.summary,
        details=payload.details,
        severity=payload.severity,
        anomaly_ids=payload.anomaly_ids,
        status="open",
    )
    INCIDENT_STORE.append(inc)
    return inc

@app.get("/incidents", response_model=List[Incident])
def list_incidents(service: Optional[str] = None, status: Optional[str] = None):
    results = INCIDENT_STORE
    if service:
        results = [i for i in results if i.service == service]
    if status:
        results = [i for i in results if i.status.lower() == status.lower()]
    return results

@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: str):
    for inc in INCIDENT_STORE:
        if inc.id == incident_id:
            return inc
    raise HTTPException(status_code=404, detail="Incident not found")

@app.patch("/incidents/{incident_id}/status", response_model=Incident)
def update_incident_status(incident_id: str, status: str):
    for inc in INCIDENT_STORE:
        if inc.id == incident_id:
            inc.status = status
            return inc
    raise HTTPException(status_code=404, detail="Incident not found")
