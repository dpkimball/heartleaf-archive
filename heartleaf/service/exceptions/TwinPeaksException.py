class TwinPeaksServiceError(Exception):
    """
    General exception to act as a base for all types of exceptions thrown
    by the TwinPeaks service.
    """
    pass


class TwinPeaksServiceAuthError(TwinPeaksServiceError):
    """Raised when the input value is too small"""
    pass


class TwinPeaksService404(TwinPeaksServiceError):
    """Raised when the input value is too large"""
    pass
