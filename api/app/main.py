from fastapi import FastAPI
from app.routes import ingest, predict
from app.core.config import settings

# new db imports
from app.db import engine, Base
from app.db import models as db_models


app = FastAPI(title="Asteria AIOps API (Phases 1-6)")

# Phase 1: ingestion
app.include_router(ingest.router, prefix="/v1")
# Phases 5 & 6: prediction + anomalies
app.include_router(predict.router, prefix="/v1")

@app.on_event("startup")
def startup_event():
    # Create DB tables if missing (safe for development)
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified")
    except Exception as e:
        print("Error creating DB tables:", e)

@app.get("/health")
async def health():
    return {"status": "ok", "project": settings.project_name}
