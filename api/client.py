from contextlib import contextmanager
import logging
from typing import Callable, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from api.config import ClientConfig

logger = logging.getLogger("automation")


class RequestHook:
    """Base request hook with no-op defaults.

    Called around every request:
    - `around_request` is a context manager wrapping the call
    - `after_response` runs once the response is back.
    Both default to no-ops, so a bare `RequestHook()` is a usable do-nothing hook,
    and subclasses only need to override the method they care about.
    """

    @contextmanager
    def around_request(self, method: str, url: str, kwargs: dict):
        yield

    def after_response(self, response: requests.Response, expect=None):
        pass


class HTTPClient:
    def __init__(
        self,
        config: ClientConfig,
        hook: Optional[RequestHook] = None,
    ):
        self._config = config
        self._hook = hook or RequestHook()
        self._session = requests.Session()

        retry_cfg = config.retry
        if retry_cfg.max_retries > 0:
            adapter = HTTPAdapter(
                max_retries=Retry(
                    total=retry_cfg.max_retries,
                    backoff_factor=retry_cfg.backoff_factor,
                    status_forcelist=retry_cfg.retry_on_status,
                    allowed_methods=list(retry_cfg.allowed_methods),
                )
            )
            self._session.mount("https://", adapter)
            self._session.mount("http://", adapter)
            logger.debug(
                f"Retry enabled: total={retry_cfg.max_retries}, "
                f"backoff={retry_cfg.backoff_factor}, "
                f"status={retry_cfg.retry_on_status}"
            )

    @property
    def session(self):
        return self._session

    def set_auth(self, auth: requests.auth.AuthBase | Callable):
        self._session.auth = auth
        logger.debug(f"Auth strategy set: {type(auth).__name__}")

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def request(
        self, method: str, path: str, *, route: Optional[dict] = None, expect=None, **kwargs
    ) -> requests.Response:
        base_url = self._config.base_url.format(**(route or {})).rstrip("/")
        url = f"{base_url}{path}"
        kwargs.setdefault("timeout", self._config.timeout)

        with self._hook.around_request(method, url, kwargs):
            logger.info(f"Request: [{method}] {url}")
            logger.debug(f"params: {kwargs.get('params')}, body: {kwargs.get('json')}")
            response = self._session.request(method, url, **kwargs)
            self._hook.after_response(response, expect)
            logger.info(f"Response: {response.status_code} ({response.elapsed.total_seconds()}s)")
        return response

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request("PATCH", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)
