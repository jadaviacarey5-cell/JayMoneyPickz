import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from modules.api_connector import (
    fetch_betrivers_props,
    fetch_injury_report,
    fetch_lineup_changes,
    fetch_prizepicks_props,
    fetch_realtime_player_stats,
    list_supported_sports,
)
from modules.decision_logic import make_pick
from modules.errors import DataUnavailableError, NoPickError
from modules.ml_model import build_feature_vector
from modules.model_selector import build_prop_model
from modules.moneyline_predictor import predict_moneyline
from modules.simulator import run_simulation

OUTPUT_DIR = Path("outputs")


def _collect_props(sport: str) -> List[Dict]:
    props = []
    try:
        props.extend(fetch_prizepicks_props(sport))
    except DataUnavailableError:
        pass
    try:
        props.extend(fetch_betrivers_props(sport))
    except DataUnavailableError:
        pass
    return props


def generate_daily_predictions(sports: List[str]) -> Dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = {"generated_at": timestamp, "sports": {}}

    for sport in sports:
        props = _collect_props(sport)
        sport_block = {
            "injuries": None,
            "lineups": None,
            "props": [],
            "moneylines": [],
        }
        try:
            sport_block["injuries"] = fetch_injury_report(sport)
        except DataUnavailableError:
            sport_block["injuries"] = None
        try:
            sport_block["lineups"] = fetch_lineup_changes(sport)
        except DataUnavailableError:
            sport_block["lineups"] = None

        for prop in props:
            player = prop.get("player")
            if not player:
                continue
            try:
                stats = fetch_realtime_player_stats(player, sport)
                feature_vector = build_feature_vector(stats)
                model = build_prop_model(sport, prop.get("prop_type"))
                model_result = model.predict(feature_vector)
                simulation = run_simulation(model_result, prop)
                pick = make_pick(simulation, prop.get("line"))
                edge = max(simulation.over_prob, simulation.under_prob) - 0.5
                sport_block["props"].append(
                    {
                        "player": player,
                        "prop_type": prop.get("prop_type"),
                        "line": prop.get("line"),
                        "pick": pick,
                        "edge": edge,
                        "simulations": simulation.simulations,
                        "over_prob": simulation.over_prob,
                        "under_prob": simulation.under_prob,
                    }
                )
            except (DataUnavailableError, NoPickError):
                continue

            try:
                moneyline_prediction = predict_moneyline(stats, prop.get("moneyline"))
            except DataUnavailableError:
                continue
            else:
                sport_block["moneylines"].append(
                    {
                        "player": player,
                        "moneyline": prop.get("moneyline"),
                        **asdict(moneyline_prediction),
                    }
                )

        payload["sports"][sport] = sport_block

    return payload


def persist_daily_predictions(sports: List[str]) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    payload = generate_daily_predictions(sports)
    date_tag = datetime.now().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"daily_predictions_{date_tag}.json"
    output_path.write_text(json.dumps(payload, indent=2))
    return output_path


def default_sports() -> List[str]:
    return list(list_supported_sports())
