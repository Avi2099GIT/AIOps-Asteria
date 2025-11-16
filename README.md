# Asteria Phase-4 TorchServe Deployment Package

Included:
- ml/models/anomaly_model.py
- ml/serving/handler.py
- ml/serving/placeholder_model.pt  (replace with real model.pt)
- scripts/save_sample_model.py    (optional helper)
- export_and_archive.sh /.ps1
- Dockerfile, entrypoint.sh
- requirements.txt

Instructions:
1. Replace ml/serving/placeholder_model.pt with your trained model state_dict or full model saved to ml/serving/model.pt.
   Recommended: save state_dict:
       python scripts/save_sample_model.py   # requires torch
   Or from your training script:
       torch.save(model.state_dict(), "ml/serving/model.pt")

2. Create MAR:
   ./export_and_archive.sh    (Linux/mac) or ./export_and_archive.ps1 (Windows PowerShell)

3. Build & run Docker:
   docker build -t asteria-torchserve:phase4 .
   docker run -p 8080:8080 -p 8081:8081 --name asteria-torchserve asteria-torchserve:phase4

Notes:
- The handler tries multiple import paths for anomaly_model to avoid ModuleNotFoundErrors.
- If you still see import errors inside torchserve, ensure the extra-files flag passed to torch-model-archiver includes the path to anomaly_model.py (we include it).
- If you want me to also generate a real .mar (requires a valid model.pt), tell me and provide the model.pt or allow me to create a minimal torch state_dict (requires torch in runtime).
