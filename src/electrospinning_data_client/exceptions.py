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

class EnvironmentMismatchError(ElectrospinningError):
    """
    Raised before a write request is sent when the token's prefix and the
    configured endpoint's environment obviously disagree (e.g. an
    `esd_sandbox_...` token used with the production API URL, or vice versa).

    This is a client-side convenience check only, based on a naming
    convention (the prefix), and is skipped whenever either side can't be
    determined (e.g. a custom `base_url` pointing at localhost). The server
    is always the authoritative check regardless of whether this exception
    fires - it validates the token's actual stored environment, not its
    prefix, and will reject a mismatched token even if this client-side
    check is somehow bypassed or wrong.
    """
    pass

class ValidationError(ElectrospinningError):
    """Raised when local validation fails (e.g., invalid filter parameters)."""
    pass

class ParsingError(ElectrospinningError):
    """Raised when there is an error parsing the API response."""
    pass
