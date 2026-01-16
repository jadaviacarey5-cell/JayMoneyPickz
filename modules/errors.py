class DataUnavailableError(RuntimeError):
    """Raised when required real-time or historical data is unavailable."""


class ModelAccuracyError(RuntimeError):
    """Raised when a model fails to meet the minimum accuracy gate."""


class NoPickError(RuntimeError):
    """Raised when the system refuses to make a pick."""
