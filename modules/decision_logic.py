"""Decision logic for recommending an over or under pick."""

from __future__ import annotations


def make_pick(results: dict, line: float) -> str:
    """Return ``"over"`` or ``"under"`` based on simulation results.

    Parameters
    ----------
    results:
        Output from :func:`modules.simulator.run_simulation`.
    line:
        The betting line supplied by the user.  Included for potential
        future logic but currently unused directly.
    """

    if results["over_prob"] >= results["under_prob"]:
        return "over"
    return "under"


__all__ = ["make_pick"]

