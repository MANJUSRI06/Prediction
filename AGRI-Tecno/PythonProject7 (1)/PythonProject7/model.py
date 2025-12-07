import torch.nn as nn
import torchvision.models as models


class SoilClassifier(nn.Module):
    def __init__(self, num_classes):
        super(SoilClassifier, self).__init__()

        self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

        # Replace last layer
        self.model.fc = nn.Linear(512, num_classes)

    def forward(self, x):
        return self.model(x)
