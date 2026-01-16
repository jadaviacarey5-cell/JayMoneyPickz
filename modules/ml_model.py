import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from modules.errors import DataUnavailableError, ModelAccuracyError


@dataclass
class ModelResult:
    mean: float
    std: float
    accuracy: float


class PropModel:
    def __init__(self, min_accuracy: float = 0.95) -> None:
        self.min_accuracy = min_accuracy
        self.coefficients: Optional[np.ndarray] = None
        self.residual_std: Optional[float] = None
        self.accuracy: Optional[float] = None

    def train(self, features: np.ndarray, targets: np.ndarray, lines: np.ndarray) -> None:
        if len(features) < 20:
            raise DataUnavailableError("At least 20 historical samples are required to train.")

        split = int(len(features) * 0.8)
        train_x, test_x = features[:split], features[split:]
        train_y, test_y = targets[:split], targets[split:]
        test_lines = lines[split:]

        self.coefficients = np.linalg.lstsq(train_x, train_y, rcond=None)[0]
        predictions = test_x @ self.coefficients
        residuals = test_y - predictions
        self.residual_std = float(np.std(residuals)) if len(residuals) else 0.0

        over_under = predictions > test_lines
        actual_over = test_y > test_lines
        accuracy = float(np.mean(over_under == actual_over)) if len(test_y) else 0.0
        self.accuracy = accuracy

        if accuracy < self.min_accuracy:
            raise ModelAccuracyError(
                f"Model accuracy {accuracy:.2%} is below the {self.min_accuracy:.0%} gate."
            )

    def predict(self, features: np.ndarray) -> ModelResult:
        if self.coefficients is None or self.residual_std is None or self.accuracy is None:
            raise DataUnavailableError("Model is not trained.")
        mean = float(features @ self.coefficients)
        return ModelResult(mean=mean, std=self.residual_std, accuracy=self.accuracy)


def load_historical_dataset(sport: str, prop_type: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    path = os.getenv("HISTORICAL_DATA_PATH")
    if not path:
        raise DataUnavailableError("HISTORICAL_DATA_PATH is not set.")

    features: List[List[float]] = []
    targets: List[float] = []
    lines: List[float] = []

    with open(path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        required = {
            "sport",
            "prop_type",
            "line",
            "actual",
            "recent_avg",
            "season_avg",
            "opponent_def_rating",
            "pace",
            "home",
            "rest_days",
            "moneyline",
            "implied_total",
        }
        if not required.issubset(reader.fieldnames or []):
            raise DataUnavailableError(
                "Historical dataset is missing required columns: "
                + ", ".join(sorted(required))
            )
        for row in reader:
            if row.get("sport", "").lower() != sport.lower():
                continue
            if row.get("prop_type") != prop_type:
                continue
            features.append(
                [
                    float(row["recent_avg"]),
                    float(row["season_avg"]),
                    float(row["opponent_def_rating"]),
                    float(row["pace"]),
                    float(row["home"]),
                    float(row["rest_days"]),
                    float(row["moneyline"]),
                    float(row["implied_total"]),
                ]
            )
            targets.append(float(row["actual"]))
            lines.append(float(row["line"]))

    if not features:
        raise DataUnavailableError("No historical rows matched the requested sport/prop.")

    return np.array(features), np.array(targets), np.array(lines)


def build_feature_vector(stats: Dict) -> np.ndarray:
    required = [
        "recent_avg",
        "season_avg",
        "opponent_def_rating",
        "pace",
        "home",
        "rest_days",
        "moneyline",
        "implied_total",
    ]
    missing = [key for key in required if key not in stats]
    if missing:
        raise DataUnavailableError(
            f"Missing real-time stat fields required for prediction: {', '.join(missing)}"
        )

    return np.array([
        float(stats["recent_avg"]),
        float(stats["season_avg"]),
        float(stats["opponent_def_rating"]),
        float(stats["pace"]),
        float(stats["home"]),
        float(stats["rest_days"]),
        float(stats["moneyline"]),
        float(stats["implied_total"]),
    ])
