
# PowerShell equivalent for Windows users
mkdir -Force ml/serving/model_store

& torch-model-archiver `
  --model-name anomaly `
  --version 1.0 `
  --serialized-file "ml/serving/model.pt" `
  --handler "ml/serving/handler.py" `
  --extra-files "ml/models/anomaly_model.py" `
  --export-path "ml/serving/model_store" `
  --force

Write-Output "Created ml/serving/model_store/anomaly.mar"
