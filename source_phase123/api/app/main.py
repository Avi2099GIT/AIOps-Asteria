from fastapi import FastAPI
from api.app.routes import ingest, predict
from api.app.core.config import settings
from routes import predict_ml
print(">>> API BOOTSTRAP =", settings.kafka_bootstrap)


app = FastAPI(title="Asteria AIOps API")

app.include_router(ingest.router, prefix="/v1")
app.include_router(predict.router, prefix="/v1")
app.include_router(predict_ml.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
