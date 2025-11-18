#!/bin/bash
set -e

echo "Starting TorchServe with authentication DISABLED"

torchserve \
  --start \
  --ncs \
  --disable-token-auth \
  --model-store /home/model-server/model_store \
  --inference-address http://0.0.0.0:8080 \
  --management-address http://0.0.0.0:8081 \
  --metrics-address http://0.0.0.0:8082

tail -f /home/model-server/logs/model_log.log
