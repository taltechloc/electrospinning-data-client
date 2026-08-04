class ElectrospinningError(Exception):
    """Base exception for all Electrospinning Client errors."""
    pass

class TransportError(ElectrospinningError):
    """Raised when a network or transport-level error occurs."""
    pass

class APIError(ElectrospinningError):
    """Raised when the API returns an error response (e.g., 4xx or 5xx)."""
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

class AuthenticationError(ElectrospinningError):
    """Raised when a write operation is attempted without a configured API token."""
    pass

class ValidationError(ElectrospinningError):
    """Raised when local validation fails (e.g., invalid filter parameters)."""
    pass

class ParsingError(ElectrospinningError):
    """Raised when there is an error parsing the API response."""
    pass
