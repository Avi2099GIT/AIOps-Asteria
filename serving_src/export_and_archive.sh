#!/usr/bin/env bash
set -euo pipefail

mkdir -p ml/serving/model_store

torch-model-archiver \
  --model-name anomaly \
  --version 1.0 \
  --serialized-file "ml/serving/model.pt" \
  --handler "ml/serving/handler.py" \
  --extra-files "ml/models/anomaly_model.py" \
  --export-path "ml/serving/model_store" \
  --force

echo "Created ml/serving/model_store/anomaly.mar"
