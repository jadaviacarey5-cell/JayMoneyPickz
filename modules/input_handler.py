import re
from typing import Dict

from modules.api_connector import list_supported_sports
from modules.errors import DataUnavailableError


PROP_PATTERN = re.compile(
    r"^(?P<player>.+?)\s+(?P<line>\d+(?:\.\d+)?)\s+(?P<prop>.+?)\s+vs\s+(?P<opponent>.+)$",
    re.IGNORECASE,
)


def parse_user_input(user_input: str) -> Dict:
    if not user_input:
        raise DataUnavailableError("Input is required.")

    match = PROP_PATTERN.match(user_input.strip())
    if not match:
        raise DataUnavailableError(
            "Input must follow: '<Player> <line> <prop> vs <Opponent>'."
        )

    parsed = match.groupdict()
    return {
        "player": parsed["player"].strip(),
        "line": float(parsed["line"]),
        "prop_type": parsed["prop"].strip(),
        "opponent": parsed["opponent"].strip(),
        "sport": None,
    }


def normalize_sport(sport: str) -> str:
    if not sport:
        raise DataUnavailableError("Sport is required.")

    normalized = sport.lower().strip()
    if normalized not in list_supported_sports():
        raise DataUnavailableError(f"Unsupported sport: {sport}.")
    return normalized
