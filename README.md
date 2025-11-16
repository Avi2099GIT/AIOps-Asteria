# Asteria — AIOps Anomaly Detection Platform (API + Serving + UI)

**Status:** Prototype / developer preview — local Docker + TorchServe based serving working.
This README is a step-by-step, **detailed** guide for running, packaging, debugging, and calling the Asteria anomaly model. It includes explicit commands for Linux/macOS and Windows PowerShell, and highlights a critical manual step: **there are two `model_store` locations** in this repo/setup and you *must copy* the generated `anomaly.mar` from one model_store to the other manually.

---

## Table of contents

* [Project layout (where things live)](#project-layout)
* [Prereqs](#prereqs)
* [1 — Prepare & package model (.mar)](#1---prepare--package-model-mar)
* [2 — Put `.mar` into both model_store locations (important)](#2---put-mar-into-both-model_store-locations-important)
* [3 — Run TorchServe (docker / docker-compose)](#3---run-torchserve-docker--docker-compose)
* [4 — Test inference (curl + PowerShell examples)](#4---test-inference-curl--powershell-examples)
* [5 — Management APIs & tokens (key_file.json)](#5---management-apis--tokens-key_filejson)
* [6 — Common problems & troubleshooting (logs & fixes)](#6---common-problems--troubleshooting-logs--fixes)
* [7 — Git tips: pushing to remote main](#7---git-tips-pushing-to-remote-main)
* [8 — Security notes & production thoughts](#8---security-notes--production-thoughts)
* [9 — Recommended next steps & checklist](#9---recommended-next-steps--checklist)
* [Appendix: Useful commands (Linux + PowerShell)](#appendix-useful-commands-linux--powershell)

---

# Project layout

(Top-level `serving/` example)

```
serving/
├─ Dockerfile
├─ docker-compose.yml?          # optional — present if you added one
├─ export_and_archive.ps1       # PowerShell helper to create anomaly.mar
├─ export_and_archive.sh        # Bash helper to create anomaly.mar
├─ ml/
│  ├─ models/
│  │  └─ anomaly_model.py       # Model class / architecture
│  └─ serving/
│     ├─ handler.py             # TorchServe handler (ASTERIA_HANDLER)
│     ├─ model.pt               # saved model (state_dict or model)
│     └─ model_store/
│        └─ anomaly.mar         # created by export script
├─ model-store/                 # second model_store location used by some builds
│  └─ anomaly.mar               # <-- copy .mar here too (manual step)
├─ requirements.txt
├─ scripts/
│  └─ save_sample_model.py
```

Handler lives at `serving/ml/serving/handler.py` (or `ml/serving/handler.py` depending on your cwd when packaging). The `export_*` scripts create `anomaly.mar` in `ml/serving/model_store/` (and sometimes in `model-store/` depending on script).

---

# Prereqs

* Docker & Docker Compose (or `docker compose` v2)
* Python 3.9+ (for packaging scripts if run locally)
* `torch-model-archiver` (packaging) — scripts typically call this (packaging via container or host)
* (Optional) `pwsh` PowerShell Core on Linux / macOS, or Windows PowerShell on Windows
* Git (for pushing repo)

---

# 1 - Prepare & package model (`.mar`)

You must create `anomaly.mar` from `model.pt` + handler + extra files. There are helper scripts in the repo.

## A: PowerShell (Windows)

1. If PowerShell warns about script execution, unblock and run once:

```powershell
# If running into security prompt the first time:
Unblock-File .\export_and_archive.ps1

# Run packaging script (choose "R" to Run once when prompted)
.\export_and_archive.ps1
```

If your environment has `pwsh` instead of Windows PowerShell, you can run:

```powershell
pwsh ./export_and_archive.ps1
```

The script should produce:

```
Created ml/serving/model_store/anomaly.mar
```

## B: Bash (Linux / macOS)

```bash
chmod +x ./export_and_archive.sh
./export_and_archive.sh
# or run python wrapper scripts if provided
```

## C: Manual `torch-model-archiver` example (if you want exact command)

If the helper script fails or you want to run archiver directly:

```bash
torch-model-archiver \
  --model-name anomaly \
  --version 1.0 \
  --serialized-file ml/serving/model.pt \
  --handler ml/serving/handler.py \
  --extra-files "ml/models/anomaly_model.py" \
  --export-path ml/serving/model_store \
  --force
```

After this you should have `ml/serving/model_store/anomaly.mar`.

---

# 2 — Put `.mar` into both `model_store` locations (**IMPORTANT**)

**There are two model_store locations** used in this workspace / Docker builds:

* `serving/ml/serving/model_store/` (where packaging script writes)
* `serving/model-store/` (another path used by a different Docker layer or local container mount)

**You must copy the generated `anomaly.mar` into the second model_store** so the running TorchServe container can see it (or copy into the container model_store directly).

### Copy on host (Linux / macOS)

```bash
# From repo root
cp serving/ml/serving/model_store/anomaly.mar serving/model-store/anomaly.mar
```

### Copy in PowerShell (Windows)

```powershell
Copy-Item -Path .\serving\ml\serving\model_store\anomaly.mar -Destination .\serving\model-store\anomaly.mar
```

### Or copy into a running TorchServe container (guaranteed to work)

Find container name (example `deploy-torchserve-1`) and run:

```bash
docker cp serving/ml/serving/model_store/anomaly.mar deploy-torchserve-1:/home/model-server/model_store/anomaly.mar
```

**Why this is necessary:** packaging and container runtime may mount or use different host paths. If `.mar` isn't in the model_store used by the container, TorchServe won't load your model.

---

# 3 — Run TorchServe (docker / docker-compose)

### A: Build Docker image (if you have a Dockerfile)

From `serving/` directory:

```bash
# Build image
docker build -t asteria-torchserve:local -f Dockerfile .

# Run container (example ports; mounts map host model_store to container model_store)
docker run -d --name deploy-torchserve-1 \
  -p 8080:8080 -p 8081:8081 -p 8082:8082 \
  -v $(pwd)/ml/serving/model_store:/home/model-server/model_store \
  -v $(pwd)/ml/serving:/home/model-server/tmp_models \
  asteria-torchserve:local
```

**Note (Windows PowerShell path style):**

```powershell
docker run -d --name deploy-torchserve-1 `
  -p 8080:8080 -p 8081:8081 -p 8082:8082 `
  -v ${PWD}\ml\serving\model_store:/home/model-server/model_store `
  -v ${PWD}\ml\serving:/home/model-server/tmp_models `
  asteria-torchserve:local
```

### B: Using `docker-compose`

If you have `docker-compose.yml` (recommended for full stack):

```bash
# build and start
docker compose up --build -d

# or with v1
docker-compose up --build -d
```

### C: Confirm TorchServe started

```bash
# ping
curl http://localhost:8080/ping

# management API (may require mgmt token)
curl http://localhost:8081/models
```

Check container logs to watch model loading:

```bash
docker logs -f deploy-torchserve-1
# look for messages like "Model loaded and eval() set." and "Model anomaly loaded."
```

---

# 4 — Test inference (curl + PowerShell examples)

TorchServe often enforces token authorization. See section 5 on how to get tokens.

## Sample request body (JSON)

We expect:

```json
{
  "embedding": [0.01, 0.01, ... up to 384 floats ...],
  "features": [1,2,3,4,5,6,7,8,9,10]
}
```

### curl (Linux/macOS)

```bash
TOKEN="aNYpc7el"   # replace with actual inference key from key_file.json

curl -X POST "http://localhost:8080/predictions/anomaly" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "embedding": [0.01, 0.01, 0.01, ...], 
    "features": [1,2,3,4,5,6,7,8,9,10]
  }'
```

### PowerShell (Windows)

```powershell
$token = "aNYpc7el"  # from key_file.json
$embedding = @(0..383 | ForEach-Object { 0.01 })
$features  = @(1,2,3,4,5,6,7,8,9,10)

$body = @{
  embedding = $embedding
  features  = $features
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/predictions/anomaly" `
  -Method Post `
  -Headers @{ "Authorization" = "Bearer $token" } `
  -Body $body `
  -ContentType "application/json"
```

**Expected output** (example):

```json
{"anomaly_score": 0.5095775127410889}
```

### Handler format caveat

* Some TorchServe handlers expect the request to be nested under `data` or expect the `body` to be a JSON string (older handler behavior).
* The provided `handler.py` contains logic that tries to accept either:

  * `data` list where each element has `.get("body")` containing a string, or
  * a direct JSON body/dict.
* If you get a `TypeError: the JSON object must be str, bytes or bytearray, not dict` — see Troubleshooting section below.

---

# 5 — Management APIs & tokens (`key_file.json`)

TorchServe by default enforces token authorization. Tokens are stored in the container at `/home/model-server/key_file.json`.

Get the file (example):

```bash
docker exec -it deploy-torchserve-1 cat /home/model-server/key_file.json
```

You will see something like:

```json
{
  "management": { "key": "dfjrQm0P", "expiration time": "2025-11-16T12:10:15.275683811Z" },
  "inference":   { "key": "aNYpc7el", "expiration time": "2025-11-16T12:10:15.275672125Z" },
  "API":         { "key": "DWIjEe-Z" }
}
```

* Use the `inference.key` (e.g., `aNYpc7el`) for inference API calls.
* Use `management.key` for management API calls (e.g., register/unregister models) when using the management port (`8081`).

**Register a model via Management API (alternative to putting .mar in model_store):**

```bash
# Management port 8081 - may require mgmt token
curl -X POST "http://localhost:8081/models?url=anomaly.mar&model_name=anomaly" \
  -H "Authorization: Bearer <management-key>"
```

---

# 6 — Common problems & troubleshooting

Below are observed issues and fixes.

### A. `InvalidKeyException` / Token Authorization failed (400)

Symptoms:

```text
"Token Authorization failed. Token either incorrect, expired, or not provided correctly"
```

Fixes:

* Confirm you added header `Authorization: Bearer <token>` exactly.
* Ensure token is valid (get fresh token from `/home/model-server/key_file.json`).
* Use correct key (inference vs management).

### B. `Prediction failed` (503) or `TypeError: JSON object must be str, bytes or bytearray, not dict`

Symptoms in worker logs:

```
TypeError: the JSON object must be str, bytes or bytearray, not dict
```

Cause:

* Handler tried `json.loads(batch)` but `batch` was already a dict (double-decoding error).
  Fix:
* Update handler to detect types robustly (example in this repo already contains logic in `preprocess()`).
* OR send body as a JSON string if your handler expects string. For example wrap body under `data`->`body` with a string.

Handler robust pattern (what this repo's handler does):

* If the incoming `body` is bytes: decode then `json.loads`.
* If it's str: `json.loads`.
* If it's dict: accept it as-is.

If you still face error, open the worker logs and inspect the exact stack trace. Example command:

```bash
docker logs deploy-torchserve-1 --tail 200
```

Look for `MODEL_LOG` `stderr`/`stdout` lines and the traceback.

### C. Model not loading or model_store mismatch

Symptoms:

* TorchServe logs show `No models found` or model not loaded.
  Fix:
* Ensure `anomaly.mar` exists in the directory mounted into container at `/home/model-server/model_store`.
* If you have multiple model_store host directories, copy `.mar` into both (see section 2).
* Alternatively `docker cp` `.mar` into container.

### D. `tail: cannot open '/home/model-server/logs/*'` when running `docker logs -f`

* TorchServe tries to tail internal logs on container start; ensure `logs` directory exists or create it in container:

  ```bash
  docker exec -it deploy-torchserve-1 mkdir -p /home/model-server/logs
  ```

### E. `pwsh` command not found on Windows (or Linux)

* Use native PowerShell on Windows; on Linux install PowerShell Core or run the `.sh` script.

---

# 7 — Git tips: pushing your first commit to remote `main`

If you ran `git push -u origin main` and received:

```
error: src refspec main does not match any
```

Likely cause: local branch name is `master` (or no branch yet). Fix:

```bash
# rename current branch to main
git branch -M main

# add remote if not set
git remote add origin https://github.com/Avi2099GIT/AIOps-Asteria.git

# push
git push -u origin main
```

Or create and push:

```bash
git checkout -b main
git push -u origin main
```

---

# 8 — Security notes & production thoughts

* **Do not** commit `/home/model-server/key_file.json` or any token/secret into git.
* For production:

  * Use Docker secrets / Kubernetes secrets / Vault for tokens and model registry credentials.
  * Turn off default `allowed_urls` to avoid loading arbitrary URLs in TorchServe (edit `config.properties`).
  * Consider building `.mar` in CI and publishing to an artifact store (S3, registry) rather than building locally on developer machine.
  * Avoid `torch.load(..., pickle=True)` on untrusted model artifacts. Use `weights_only=True` where appropriate and follow PyTorch security guidance.

---

# 9 — Recommended next steps & checklist

1. ✅ Generate `anomaly.mar` via `export_and_archive` script.
2. ✅ Copy `anomaly.mar` to the second model_store path (manual step).
3. ✅ Start container / compose and confirm TorchServe logs show model loaded.
4. ✅ Get inference key from `/home/model-server/key_file.json`.
5. ✅ Test inference via `curl` or PowerShell (examples above).
6. Add a `docker-compose.yml` (if not present) that mounts correct `model_store` and exposes ports.
7. Automate `.mar` creation and copy into model_store in CI.
8. Replace tokens with secret management and harden config for production.

---

# Appendix — Useful commands (Linux / macOS / PowerShell)

### Docker & compose

```bash
docker build -t asteria-torchserve:local -f Dockerfile .
docker run -d --name deploy-torchserve-1 -p 8080:8080 -p 8081:8081 -p 8082:8082 \
  -v $(pwd)/ml/serving/model_store:/home/model-server/model_store \
  asteria-torchserve:local

docker logs -f deploy-torchserve-1
docker cp ml/serving/model_store/anomaly.mar deploy-torchserve-1:/home/model-server/model_store/anomaly.mar
docker exec -it deploy-torchserve-1 cat /home/model-server/key_file.json
```

### curl inference

```bash
TOKEN="aNYpc7el"
curl -X POST "http://localhost:8080/predictions/anomaly" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"embedding":[0.01,0.01,...],"features":[1,2,3,4,5,6,7,8,9,10]}'
```

### PowerShell

```powershell
$token = "aNYpc7el"
$embedding = @(0..383 | ForEach-Object { 0.01 })
$features  = @(1,2,3,4,5,6,7,8,9,10)
$body = @{ embedding = $embedding; features = $features } | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/predictions/anomaly" -Method Post `
  -Headers @{ "Authorization" = "Bearer $token" } -Body $body -ContentType "application/json"
```

### Model archiver (manual)

```bash
torch-model-archiver --model-name anomaly --version 1.0 \
  --serialized-file ml/serving/model.pt \
  --handler ml/serving/handler.py \
  --extra-files "ml/models/anomaly_model.py" \
  --export-path ml/serving/model_store --force
```

---

