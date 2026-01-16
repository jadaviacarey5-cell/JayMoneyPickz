from dataclasses import dataclass
from typing import Dict, Optional

from modules.errors import DataUnavailableError


@dataclass
class MoneylinePrediction:
    win_probability: float
    implied_probability: float
    edge: float


def moneyline_to_implied_prob(moneyline: float) -> float:
    if moneyline == 0:
        raise DataUnavailableError("Moneyline cannot be zero.")
    if moneyline > 0:
        return 100 / (moneyline + 100)
    return abs(moneyline) / (abs(moneyline) + 100)


def predict_moneyline(stats: Dict, moneyline: Optional[float]) -> MoneylinePrediction:
    if moneyline is None:
        raise DataUnavailableError("Moneyline is required for prediction.")
    if "win_prob" not in stats:
        raise DataUnavailableError("Real-time win_prob is required for moneyline prediction.")

    win_prob = float(stats["win_prob"])
    implied = moneyline_to_implied_prob(float(moneyline))
    edge = win_prob - implied

    return MoneylinePrediction(
        win_probability=win_prob,
        implied_probability=implied,
        edge=edge,
    )
