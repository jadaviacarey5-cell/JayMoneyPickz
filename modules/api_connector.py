"""Utility functions for retrieving real-time sports data.

Currently this module provides a small wrapper around the free
``balldontlie`` API for NBA statistics.  The function
``fetch_player_stats`` can be used by the simulator to obtain the most
recent season averages for a given player and statistic.  The API does
not require authentication which makes it suitable for small demo
applications and tests.

Example
-------
>>> fetch_player_stats("LeBron James", "pts")
27.0

The function raises ``ValueError`` if the player or stat cannot be
found, allowing the caller to handle the error and provide feedback to
the user.
"""

from __future__ import annotations

import requests

BASE_URL_NBA = "https://www.balldontlie.io/api/v1"


def fetch_player_stats(player_name: str, stat: str, sport: str = "nba") -> float:
    """Fetch a player's season average for a given statistic.

    Parameters
    ----------
    player_name:
        Name of the athlete, e.g. ``"LeBron James"``.
    stat:
        Abbreviation of the statistic to fetch (``"pts"``, ``"reb"``, ``"ast"`` ...).
    sport:
        Identifier of the sport.  Only ``"nba"`` is supported at the
        moment as it maps cleanly to the ``balldontlie`` API.

    Returns
    -------
    float
        The season average for the requested statistic.

    Raises
    ------
    ValueError
        If the player or stat cannot be resolved.
    """

    if sport.lower() != "nba":
        raise ValueError("Only 'nba' is supported for real-time data")

    # Step 1: look up the player's ID
    response = requests.get(
        f"{BASE_URL_NBA}/players", params={"search": player_name}, timeout=10
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("data"):
        raise ValueError(f"Player '{player_name}' not found")

    player_id = payload["data"][0]["id"]

    # Step 2: query season averages for that player
    stats_response = requests.get(
        f"{BASE_URL_NBA}/season_averages",
        params={"player_ids[]": player_id},
        timeout=10,
    )
    stats_response.raise_for_status()
    stats_payload = stats_response.json()
    if not stats_payload.get("data"):
        raise ValueError(f"No stats available for player '{player_name}'")

    stat_value = stats_payload["data"][0].get(stat.lower())
    if stat_value is None:
        raise ValueError(f"Stat '{stat}' not available for player '{player_name}'")

    return float(stat_value)


__all__ = ["fetch_player_stats"]

