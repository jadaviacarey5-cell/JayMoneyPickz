from dataclasses import dataclass
from typing import Dict

from modules.api_connector import fetch_realtime_player_stats
from modules.errors import DataUnavailableError
from modules.ml_model import PropModel, build_feature_vector, load_historical_dataset


@dataclass
class ModelBundle:
    model: PropModel
    features: Dict


def build_prop_model(sport: str, prop_type: str) -> PropModel:
    features, targets, lines = load_historical_dataset(sport, prop_type)
    model = PropModel(min_accuracy=0.95)
    model.train(features, targets, lines)
    return model


def select_model(parsed: Dict) -> ModelBundle:
    sport = parsed.get("sport")
    prop_type = parsed.get("prop_type")
    player = parsed.get("player")

    if not sport:
        raise DataUnavailableError("Sport must be provided to select a model.")

    model = build_prop_model(sport, prop_type)
    stats = fetch_realtime_player_stats(player, sport)
    features = build_feature_vector(stats)

    return ModelBundle(model=model, features={"vector": features, "stats": stats})
