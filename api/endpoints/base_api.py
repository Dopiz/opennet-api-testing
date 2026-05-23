import requests

from api.client import HTTPClient


class BaseAPI:
    version = "v1"
    component = ""

    def __init__(self, client: HTTPClient):
        self._client = client

    @property
    def _route(self) -> dict:
        """Values that fill the base_url template."""
        return {"version": self.version, "component": self.component}

    def _get(self, path: str, **kwargs) -> requests.Response:
        return self._client.get(path, route=self._route, **kwargs)

    def _post(self, path: str, **kwargs) -> requests.Response:
        return self._client.post(path, route=self._route, **kwargs)

    def _put(self, path: str, **kwargs) -> requests.Response:
        return self._client.put(path, route=self._route, **kwargs)

    def _patch(self, path: str, **kwargs) -> requests.Response:
        return self._client.patch(path, route=self._route, **kwargs)

    def _delete(self, path: str, **kwargs) -> requests.Response:
        return self._client.delete(path, route=self._route, **kwargs)
