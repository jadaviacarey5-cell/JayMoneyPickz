from typing import Dict, List

from modules.api_connector import (
    fetch_betrivers_props,
    fetch_prizepicks_props,
    fetch_realtime_player_stats,
)
from modules.decision_logic import make_pick
from modules.errors import DataUnavailableError, NoPickError
from modules.ml_model import build_feature_vector
from modules.model_selector import build_prop_model
from modules.simulator import run_simulation


MAX_SLIPS = 6


def _merge_props(prizepicks: List[Dict], betrivers: List[Dict]) -> List[Dict]:
    return prizepicks + betrivers


def generate_top_slips(sport: str) -> List[Dict]:
    prizepicks = fetch_prizepicks_props(sport)
    betrivers = fetch_betrivers_props(sport)
    props = _merge_props(prizepicks, betrivers)

    if not props:
        raise DataUnavailableError("No props found for the selected sport.")

    picks: List[Dict] = []
    for prop in props:
        prop_type = prop.get("prop_type")
        model = build_prop_model(sport, prop_type)
        player = prop.get("player")
        if not player:
            continue
        try:
            stats = fetch_realtime_player_stats(player, sport)
            feature_vector = build_feature_vector(stats)
        except DataUnavailableError:
            continue

        model_result = model.predict(feature_vector)
        sim = run_simulation(model_result, prop)
        try:
            pick = make_pick(sim, prop["line"])
        except NoPickError:
            continue

        edge = max(sim.over_prob, sim.under_prob) - 0.5
        picks.append(
            {
                "pick": pick,
                "player": prop.get("player"),
                "line": prop.get("line"),
                "prop_type": prop.get("prop_type"),
                "edge": edge,
            }
        )

    picks.sort(key=lambda item: item["edge"], reverse=True)
    return picks[:MAX_SLIPS]
