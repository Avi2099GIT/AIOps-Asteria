# Optional helper: saves a sample AnomalyLSTM state_dict as model.pt
# Requires torch to be installed in the environment where you run it.
import torch
from ml.models.anomaly_model import AnomalyLSTM

def main():
    model = AnomalyLSTM()
    torch.save(model.state_dict(), "ml/serving/model.pt")
    print("Saved sample state_dict to ml/serving/model.pt")

if __name__ == "__main__":
    main()
