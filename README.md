
# Asteria - Integrated AIOps Platform (Phases 1–6)

This repository now integrates:

- Phase 1–3: Ingestion, embeddings, and training (from your original backend assets).
- Phase 4: TorchServe-based anomaly model serving.
- Phase 5: AIOps API layer (FastAPI) for logs, anomalies, incidents.
- Phase 6: Basic AIOps dashboard (Streamlit) wired to the API.

## Run everything

```bash
cd deploy
docker-compose up --build
```

- API: http://localhost:8000
- TorchServe: http://localhost:8080
- Dashboard: http://localhost:8501
\n
## Phases 5 & 6 (Integrated here)

- **Phase 5 – API & Integration**
  - `/v1/events` – ingest raw events (Phase 1 entrypoint).
  - `/v1/predict/anomaly` – main anomaly scoring endpoint that:
    - Builds an embedding from the log text (384-dim placeholder).
    - Fetches rolling features via Redis (`FeatureClient`).
    - Calls TorchServe (`/predictions/anomaly`) with `embedding + features`.
    - Returns anomaly score, severity, confidence, and recommended actions.

- **Phase 6 – Full Pipeline & Dashboard**
  - `/v1/anomalies/recent` – reads from the anomaly log file and returns recent anomalies.
  - `dashboard/app.py` – a Streamlit dashboard that can:
    - Trigger anomaly scoring from UI.
    - Visualize recent anomalies.
  - `deploy/docker-compose.yml` has a `dashboard` service exposing `http://localhost:8501`.

## Frontend

A modern React + Vite frontend was added under `frontend/`. Run `npm install` then `npm run dev`.
