from contextlib import contextmanager
import json
from typing import List

import allure
import requests

from api.client import RequestHook


class CompositeRequestHook:
    def __init__(self, *hooks: List[RequestHook]):
        self._hooks = hooks

    @contextmanager
    def around_request(self, method: str, url: str, kwargs: dict):
        cms = [hook.around_request(method, url, kwargs) for hook in self._hooks]
        for cm in cms:
            cm.__enter__()
        try:
            yield
        finally:
            for cm in reversed(cms):
                cm.__exit__(None, None, None)

    def after_response(self, response: requests.Response, expect=None) -> None:
        for hook in self._hooks:
            hook.after_response(response, expect)


class AllureReportHook(RequestHook):
    @contextmanager
    def around_request(self, method: str, url: str, kwargs: dict):
        with allure.step(f"[{method}] {url}"):
            payload = kwargs.get("json") or kwargs.get("data")
            if payload is not None:
                body = (
                    json.dumps(payload, indent=2, ensure_ascii=False)
                    if isinstance(payload, (dict, list))
                    else str(payload)
                )
                allure.attach(body, name="Request Body", attachment_type=allure.attachment_type.JSON)

            params = kwargs.get("params")
            if params is not None:
                allure.attach(
                    json.dumps(params, indent=2, ensure_ascii=False),
                    name="Query Params",
                    attachment_type=allure.attachment_type.JSON,
                )

            yield

    def after_response(self, response: requests.Response, expect=None) -> None:
        try:
            body = json.dumps(response.json(), indent=2, ensure_ascii=False)
            attachment_type = allure.attachment_type.JSON
        except (json.JSONDecodeError, ValueError):
            body = response.text[:5000]
            attachment_type = allure.attachment_type.TEXT

        allure.attach(body, name=f"Response [{response.status_code}]", attachment_type=attachment_type)
