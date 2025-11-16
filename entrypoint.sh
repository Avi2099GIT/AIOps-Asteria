#!/usr/bin/env bash
set -e
if [ -d "ml/serving/model_store" ]; then
  cp ml/serving/model_store/*.mar /home/model-server/model_store/ 2>/dev/null || true
fi
torchserve --start --model-store model_store --models anomaly=anomaly.mar --ts-config /home/model-server/config.properties || true
tail -f /home/model-server/logs/* || sleep infinity
