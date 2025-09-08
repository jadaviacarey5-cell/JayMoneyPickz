"""Model selection helpers.

The original project hints at multiple models depending on the sport.
For now this module simply exposes :func:`select_model` which returns
``None``.  The function exists so that :mod:`app` can import it without
failing and it provides a clean extension point for future work.
"""

from __future__ import annotations


def select_model(sport: str):
    """Return a model object for ``sport``.

    The real application might return different trained models for each
    sport.  The simulator implemented in this challenge does not require
    a model, so ``None`` is returned.
    """

    return None


__all__ = ["select_model"]

