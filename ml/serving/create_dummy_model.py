import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import torch
from ml.models.anomaly_model import AnomalyLSTM

# Model architecture MUST match handler exactly
model = AnomalyLSTM(
    embedding_dim=384,
    feature_dim=10,
    hidden=128
)

# Initialize with random weights
state_dict = model.state_dict()

# Save the correct state_dict
output_path = os.path.join(os.path.dirname(__file__), "model.pt")
torch.save(state_dict, output_path)


print("Generated valid model.pt for AnomalyLSTM")
