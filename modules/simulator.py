"""Simple Monte Carlo simulator for player props.

The simulator pulls real-time player averages using the helper in
``api_connector`` and runs a Monte Carlo simulation to estimate the
probability of a player going over or under a specific line.
"""

from __future__ import annotations

import numpy as np

from .api_connector import fetch_player_stats


def run_simulation(model, parsed: dict) -> dict:
    """Run a Monte Carlo simulation for a player prop.

    Parameters
    ----------
    model:
        Placeholder for future model selection.  Currently unused.
    parsed:
        Dictionary containing at least ``player``, ``line`` and
        ``prop_type``.  Optional keys are ``sport`` (default ``"nba"``)
        and ``sims`` (number of simulations, default ``10000``).

    Returns
    -------
    dict
        A dictionary with the mean statistic and the probabilities for
        the over and under outcomes.
    """

    player = parsed["player"]
    line = float(parsed["line"])
    prop_type = parsed["prop_type"].lower()
    sport = parsed.get("sport", "nba")
    sims = int(parsed.get("sims", 10000))

    # Mapping from human-readable prop to API stat key
    stat_map = {"points": "pts", "rebounds": "reb", "assists": "ast"}
    stat_key = stat_map.get(prop_type)
    if stat_key is None:
        raise ValueError(f"Unsupported prop type '{prop_type}'")

    mean = fetch_player_stats(player, stat_key, sport)

    # The true standard deviation would require more detailed data.  A
    # simple constant keeps the example deterministic and easy to test.
    samples = np.random.normal(mean, 1.5, sims)
    over_prob = float(np.mean(samples > line))
    under_prob = 1 - over_prob

    return {"mean": float(mean), "over_prob": over_prob, "under_prob": under_prob}


__all__ = ["run_simulation"]

