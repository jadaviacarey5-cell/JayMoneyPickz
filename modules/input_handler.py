"""Parsing helpers for user input.

The Streamlit interface expects the user to type a string describing the
prop they wish to simulate.  The :func:`parse_user_input` function turns
this free-form string into a structured dictionary consumed by the
simulator.
"""

from __future__ import annotations

import re


_INPUT_RE = re.compile(
    r"^(?P<player>.+?)\s+(?P<line>\d+\.?\d*)\s+(?P<prop_type>\w+)$",
    re.IGNORECASE,
)


def parse_user_input(user_input: str) -> dict:
    """Parse a user supplied prop description.

    The expected format is ``"Player Name 24.5 points"``.  Only the
    player name, line and prop type are required; the sport is currently
    fixed to ``"nba"`` because the real-time API connector only supports
    NBA data.

    Parameters
    ----------
    user_input:
        Raw string provided by the user.

    Returns
    -------
    dict
        A dictionary with keys: ``player``, ``line``, ``prop_type``,
        ``sport`` and ``sims``.
    """

    match = _INPUT_RE.match(user_input.strip())
    if not match:
        raise ValueError(
            "Input must be of the form 'Player Name <line> <prop_type>'"
        )

    data = match.groupdict()
    data["line"] = float(data["line"])
    data["prop_type"] = data["prop_type"].lower()
    data["sport"] = "nba"  # Only NBA is supported for now
    data["sims"] = 10000
    return data


__all__ = ["parse_user_input"]

