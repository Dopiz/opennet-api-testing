import logging
import time

import requests

logger = logging.getLogger("automation")


class APIKeyAuth(requests.auth.AuthBase):
    """Attaches the api-sports `x-apisports-key` header to every request."""

    def __init__(self, api_key: str, expires_at: int = None, refresh_buffer: int = 60, ttl: int = 3600):
        if not api_key:
            logger.warning("APIKeyAuth created without an API key, requests might be rejected (set TEST_API_KEY).")
        self._api_key = api_key
        self.expires_at = expires_at
        self.refresh_buffer = refresh_buffer
        self.ttl = ttl

    def _ensure_validate(self) -> None:
        if self._api_key is None or (self.expires_at and time.time() >= self.expires_at - self.refresh_buffer):
            # Token refresh / re-login (e.g. call a login API) would go here, then update new expiry time.
            self.expires_at = time.time() + self.ttl

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        self._ensure_validate()
        request.headers["x-apisports-key"] = self._api_key
        return request
