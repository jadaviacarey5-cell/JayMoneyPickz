from modules.errors import NoPickError
from modules.simulator import SimulationResult


MIN_EDGE = 0.05


def make_pick(result: SimulationResult, line: float) -> str:
    if result.over_prob > 0.5 + MIN_EDGE:
        return "over"
    if result.under_prob > 0.5 + MIN_EDGE:
        return "under"
    raise NoPickError(
        "No edge above 5% was found. The system refuses to guess without an edge."
    )
