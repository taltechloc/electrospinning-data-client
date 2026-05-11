import requests
from abc import ABC, abstractmethod
from typing import Any, Optional
from .exceptions import APIError, TransportError


class Transport(ABC):
    """Abstract base class for HTTP communication."""
    
    @abstractmethod
    def request(self, method: str, url: str, **kwargs) -> Any:
        """Perform an HTTP request."""
        pass

class RequestsTransport(Transport):
    """
    Concrete implementation of Transport using the requests library.
    Uses a requests.Session for connection pooling and efficient resource usage.
    """

    def __init__(self, timeout: int = 60, verify: bool = True):
        self.timeout = timeout
        self.verify = verify
        self._session = requests.Session()

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Perform an HTTP request with built-in error handling and
        timeout management.
        """
        try:
            # Set default timeout if not provided
            kwargs.setdefault('timeout', self.timeout)
            kwargs.setdefault('verify', self.verify)

            response = self._session.request(method, url, **kwargs)

            if not response.ok:
                self._handle_error(response)

            return response
        except requests.RequestException as e:
            raise TransportError(f"Network error occurred: {str(e)}") from e

    def _handle_error(self, response: requests.Response) -> None:
        """Parse API error responses and raise appropriate exceptions."""
        try:
            error_data = response.json()
            # Try to get a descriptive error message from the JSON response
            error_msg = (
                error_data.get("error") or
                error_data.get("message") or
                response.text
            )
        except (ValueError, AttributeError):
            error_msg = response.text

        raise APIError(
            f"API request failed ({response.status_code}): {error_msg}",
            status_code=response.status_code,
            response_body=response.text
        )

    def close(self) -> None:
        """Close the underlying requests session."""
        self._session.close()
