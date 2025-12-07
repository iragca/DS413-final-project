from pathlib import Path

import torch

from .cnn import SimpleCNN


class DoubleModelApproach:
    def __init__(
        self,
        disease_detection_state,
        symptom_identifier_state,
        threshold: float = 0.5,
        device: torch.device = torch.device("cpu"),
    ):
        self.disease_detector = SimpleCNN(channels=3, output_dim=1)
        self.disease_detector.load_state_dict(
            torch.load(Path(disease_detection_state), map_location=device)
        )
        self.disease_detector.to(device)
        self.disease_detector.eval()
        self.symptom_identifier = SimpleCNN(channels=3, output_dim=12)
        self.symptom_identifier.load_state_dict(
            torch.load(Path(symptom_identifier_state), map_location=device)
        )
        self.symptom_identifier.to(device)
        self.symptom_identifier.eval()
        self.threshold = threshold
        self.device = device

    def __call__(self, images):
        preds = []

        for img in images:
            img = img.unsqueeze(0)  # Add batch dimension
            disease_pred = self._detect_disease(img)
            if disease_pred.item() == 1:
                symptom_pred = self._identify_symptoms(img)
                preds.append(symptom_pred.item())
            else:
                preds.append(12)  # No disease detected
        return torch.tensor(preds)

    def _detect_disease(self, images):
        images = images.to(self.device)
        with torch.no_grad():
            preds = self.disease_detector(images)
            preds = (preds >= self.threshold).long()
        return preds.cpu()

    def _identify_symptoms(self, images):
        images = images.to(self.device)
        with torch.no_grad():
            preds = self.symptom_identifier(images)
            preds = preds.argmax(dim=1)
        return preds.cpu()
