from dataclasses import dataclass
from typing import Dict

import numpy as np

from modules.errors import DataUnavailableError
from modules.ml_model import ModelResult


@dataclass
class SimulationResult:
    mean: float
    std: float
    over_prob: float
    under_prob: float
    accuracy: float
    simulations: int


def run_monte_carlo(model_result: ModelResult, line: float, simulations: int = 20000) -> SimulationResult:
    if simulations <= 0:
        raise ValueError("Simulations must be positive.")

    rng = np.random.default_rng()
    samples = rng.normal(loc=model_result.mean, scale=model_result.std, size=simulations)
    over_prob = float(np.mean(samples > line))
    under_prob = float(np.mean(samples < line))

    return SimulationResult(
        mean=model_result.mean,
        std=model_result.std,
        over_prob=over_prob,
        under_prob=under_prob,
        accuracy=model_result.accuracy,
        simulations=simulations,
    )


def run_simulation(model_result: ModelResult, prop: Dict, simulations: int = 20000) -> SimulationResult:
    if model_result is None:
        raise DataUnavailableError("Model output is required for simulation.")
    line = float(prop.get("line"))
    return run_monte_carlo(model_result, line=line, simulations=simulations)
