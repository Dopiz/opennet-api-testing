from dataclasses import dataclass
from typing import Optional, Union

import requests

from api.client import RequestHook


@dataclass
class Expect:
    """Per-call validation expectations. Pass to an API call to override defaults;
    leave a field as None to fall back to the validator's configured default.
    """

    status: Optional[Union[int, list[int]]] = None
    max_time: Optional[float] = None


class StatusValidator(RequestHook):
    """Assert the response status code.

    - no per-call ``Expect.status`` → must be in ``allowed_status`` (config default)
    - ``Expect(status=404)`` / ``Expect(status=[400, 404])`` → must match exactly
    """

    def __init__(self, allowed_status: Optional[list[int]] = None):
        self._allowed = list(allowed_status) if allowed_status else list(range(200, 400))

    def _normalize(self, status: Union[int, list[int]]) -> list[int]:
        return [status] if isinstance(status, int) else list(status)

    def after_response(self, response: requests.Response, expect: Optional[Expect] = None) -> None:
        allowed = self._normalize(expect.status) if (expect and expect.status is not None) else self._allowed
        assert response.status_code in allowed, (
            f"Expected status {allowed}, got {response.status_code} "
            f"for [{response.request.method}] {response.request.url}"
        )


class ResponseTimeValidator(RequestHook):
    """Assert the response time is within a threshold.

    - no per-call ``Expect.max_time`` → use ``default_max`` (config default)
    - ``Expect(max_time=1.5)`` → override for this call
    - threshold None → skip
    """

    def __init__(self, default_max: Optional[float] = None):
        self._default_max = default_max

    def after_response(self, response: requests.Response, expect: Optional[Expect] = None) -> None:
        limit = expect.max_time if (expect and expect.max_time is not None) else self._default_max
        if limit is None:
            return
        elapsed = response.elapsed.total_seconds()
        assert elapsed <= limit, (
            f"Response time {elapsed:.3f}s exceeded {limit}s for [{response.request.method}] {response.request.url}"
        )
