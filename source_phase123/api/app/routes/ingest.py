from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from api.app.services.producer import produce_event


router = APIRouter()

class IngestPayload(BaseModel):
    event_id: str
    timestamp: str
    tenant_id: str
    source: str
    service: str
    environment: str
    type: str
    payload: Dict[str, Any]

@router.post('/events')
async def ingest(payload: IngestPayload, authorization: Optional[str] = Header(None), x_tenant_id: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail='missing auth')
    # validate tenant header (simple check)
    if x_tenant_id is None or x_tenant_id != payload.tenant_id:
        raise HTTPException(status_code=400, detail='X-Tenant-ID mismatch')
    await produce_event(payload.dict())
    return {"status": "queued"}
