import torch
import torch.nn as nn

class AnomalyLSTM(nn.Module):
    def __init__(self, embedding_dim=384, feature_dim=10, hidden=128):
        super().__init__()
        self.lstm = nn.LSTM(embedding_dim + feature_dim, hidden, batch_first=True)
        self.fc = nn.Linear(hidden, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        out = self.fc(out)
        return self.sigmoid(out)
