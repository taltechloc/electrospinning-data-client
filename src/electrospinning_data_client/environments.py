"""
Named environments for the Electrospinning Data API. Two environments are
deployed: Sandbox (for development/integration testing - isolated, disposable
data) and Production (real submissions, real moderation workflow). A token
only ever authenticates in the environment it was issued for; the server is
the authoritative check, but this module also lets the client catch an
obvious mismatch before making a network call at all.
"""
from typing import Optional
from urllib.parse import urlsplit

SANDBOX = "sandbox"
PRODUCTION = "production"

_ENVIRONMENT_URLS = {
    SANDBOX: {
        "base_url": "https://sandbox-api.electrospinning-data.org/public/dataset",
        "api_base_url": "https://sandbox-api.electrospinning-data.org",
    },
    PRODUCTION: {
        "base_url": "https://api.electrospinning-data.org/public/dataset",
        "api_base_url": "https://api.electrospinning-data.org",
    },
}

# Preserves the exact default new Client() has always had, for callers who
# pass neither `base_url` nor `environment` -- existing read-only usage is
# never silently redirected.
DEFAULT_BASE_URL = _ENVIRONMENT_URLS[PRODUCTION]["base_url"]

SANDBOX_TOKEN_PREFIX = "esd_sandbox_"
PRODUCTION_TOKEN_PREFIX = "esd_pat_"


def resolve_urls(environment: str):
    """Returns (base_url, api_base_url) for a named environment, or raises ValueError."""
    key = environment.strip().lower() if environment else ""
    if key not in _ENVIRONMENT_URLS:
        raise ValueError(
            f"environment must be one of {list(_ENVIRONMENT_URLS)!r}, got {environment!r}"
        )
    urls = _ENVIRONMENT_URLS[key]
    return urls["base_url"], urls["api_base_url"]


def infer_environment_from_token(token: Optional[str]) -> Optional[str]:
    """Best-effort, prefix-based guess. None if the token doesn't look like either prefix."""
    if not token:
        return None
    if token.startswith(SANDBOX_TOKEN_PREFIX):
        return SANDBOX
    if token.startswith(PRODUCTION_TOKEN_PREFIX):
        return PRODUCTION
    return None


def infer_environment_from_url(url: Optional[str]) -> Optional[str]:
    """
    Best-effort guess from a host name. Matches only the two actual deployed
    hosts (not a broad "starts with api." pattern) so it stays silent for
    anything else -- localhost during development, a mock server in tests, a
    self-hosted proxy -- rather than guessing and risking a false positive.
    """
    if not url:
        return None
    host = urlsplit(url).netloc.lower()
    for environment, urls in _ENVIRONMENT_URLS.items():
        if host == urlsplit(urls["api_base_url"]).netloc.lower():
            return environment
    return None
