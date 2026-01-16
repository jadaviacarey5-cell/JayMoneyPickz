import os
from typing import Dict, Iterable, List, Optional

import requests

from modules.errors import DataUnavailableError

PRIZEPICKS_API = "https://api.prizepicks.com/projections"


def _get_json(url: str, params: Optional[Dict[str, str]] = None) -> Dict:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def fetch_prizepicks_props(sport: Optional[str] = None) -> List[Dict]:
    params = {"per_page": 250, "single_stat": "true"}
    payload = _get_json(PRIZEPICKS_API, params=params)
    data = payload.get("data", [])
    included = payload.get("included", [])

    players = {item["id"]: item["attributes"] for item in included if item["type"] == "player"}
    leagues = {item["id"]: item["attributes"] for item in included if item["type"] == "league"}

    props: List[Dict] = []
    for entry in data:
        attributes = entry.get("attributes", {})
        relationships = entry.get("relationships", {})
        player_rel = relationships.get("new_player", {}).get("data")
        league_rel = relationships.get("league", {}).get("data")

        if not player_rel or not league_rel:
            continue

        player = players.get(player_rel["id"], {})
        league = leagues.get(league_rel["id"], {})
        sport_name = league.get("sport", "").lower()
        if sport and sport_name != sport.lower():
            continue

        props.append(
            {
                "source": "prizepicks",
                "projection_id": entry.get("id"),
                "player": player.get("name"),
                "team": player.get("team"),
                "sport": sport_name,
                "league": league.get("name"),
                "prop_type": attributes.get("stat_type"),
                "line": attributes.get("line_score"),
                "start_time": attributes.get("start_time"),
            }
        )

    if not props:
        raise DataUnavailableError("PrizePicks returned no projections for the requested sport.")

    return props


def fetch_betrivers_props(sport: Optional[str] = None) -> List[Dict]:
    api_url = os.getenv("BETRIVERS_API_URL")
    if not api_url:
        raise DataUnavailableError(
            "BETRIVERS_API_URL is not set. Provide a real-time Betrivers endpoint."
        )

    payload = _get_json(api_url, params={"sport": sport} if sport else None)
    props = payload.get("props", [])
    if not props:
        raise DataUnavailableError("Betrivers returned no props for the requested sport.")

    normalized = []
    for item in props:
        normalized.append(
            {
                "source": "betrivers",
                "projection_id": item.get("id"),
                "player": item.get("player"),
                "team": item.get("team"),
                "sport": item.get("sport", "").lower(),
                "league": item.get("league"),
                "prop_type": item.get("prop_type"),
                "line": item.get("line"),
                "start_time": item.get("start_time"),
                "moneyline": item.get("moneyline"),
            }
        )
    return normalized


def fetch_realtime_player_stats(player: str, sport: str) -> Dict:
    stats_url = os.getenv("STATS_API_URL")
    if not stats_url:
        raise DataUnavailableError(
            "STATS_API_URL is not set. Provide a real-time stats endpoint."
        )

    payload = _get_json(
        stats_url,
        params={
            "sport": sport,
            "player": player,
        },
    )
    stats = payload.get("stats")
    if not stats:
        raise DataUnavailableError(f"No real-time stats found for {player} in {sport}.")

    return stats


def fetch_injury_report(sport: str) -> Dict:
    injuries_url = os.getenv("INJURIES_API_URL")
    if not injuries_url:
        raise DataUnavailableError(
            "INJURIES_API_URL is not set. Provide a real-time injury feed endpoint."
        )

    payload = _get_json(injuries_url, params={"sport": sport})
    injuries = payload.get("injuries")
    if not injuries:
        raise DataUnavailableError(f"No injury data found for {sport}.")
    return injuries


def fetch_lineup_changes(sport: str) -> Dict:
    lineups_url = os.getenv("LINEUPS_API_URL")
    if not lineups_url:
        raise DataUnavailableError(
            "LINEUPS_API_URL is not set. Provide a real-time lineup feed endpoint."
        )

    payload = _get_json(lineups_url, params={"sport": sport})
    lineups = payload.get("lineups")
    if not lineups:
        raise DataUnavailableError(f"No lineup data found for {sport}.")
    return lineups


def list_supported_sports() -> Iterable[str]:
    static_sports = {"mlb", "tennis", "wnba", "soccer", "pga", "cs2", "lol", "val"}
    return sorted(static_sports)
