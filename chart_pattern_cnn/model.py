# chart_pattern_cnn/model.py
"""
PyTorch CNN for Chart Pattern Detection (Head and Shoulders Example)
Based on: Deep Learning for Identifying Technical Chart Patterns
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

class ChartPatternCNN(nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()
        self.conv1 = nn.Conv1d(1, 16, kernel_size=5, stride=1, padding=2)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=5, stride=1, padding=2)
        self.pool = nn.MaxPool1d(2)
        self.fc1 = nn.Linear(32 * 25, 64)
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x):
        # x shape: (batch, 1, window_length)
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Example usage:
# model = ChartPatternCNN(num_classes=2)  # 2 classes: head-and-shoulders, no-pattern
# output = model(torch.randn(8, 1, 100))  # batch of 8 windows, each 100 timesteps
