"""Placeholder slip generator.

This module is outside the scope of the real-time data feature.  It
exposes a ``generate_top_slips`` function returning an empty list so the
Streamlit app can import and call it without additional logic.
"""

from __future__ import annotations


def generate_top_slips(sport: str):
    """Return an empty list of slips.

    In a full implementation this function would analyse available props
    and return the most valuable slips.  Returning an empty list keeps
    the interface functional for the purposes of this challenge.
    """

    return []


__all__ = ["generate_top_slips"]

