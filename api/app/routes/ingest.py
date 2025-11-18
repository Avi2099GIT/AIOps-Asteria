
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.producer import produce_event


router = APIRouter(tags=["ingest"])

class IngestPayload(BaseModel):
    event_id: str
    timestamp: str
    tenant_id: str
    source: str
    service: str
    environment: str
    type: str
    payload: Dict[str, Any]

@router.post("/events")
async def ingest_event(
    payload: IngestPayload,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
):
    """Phase 1: Ingest raw events into the pipeline.

    - Performs a basic auth header check (only presence, not validation).
    - Enforces that `X-Tenant-ID` matches the payload's `tenant_id`.
    - Pushes the event to Kafka (or local file fallback) via `produce_event`.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if x_tenant_id is None or x_tenant_id != payload.tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID mismatch")

    await produce_event(payload.dict())
    return {"status": "queued"}
