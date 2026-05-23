import allure
import pytest

from api.auth import APIKeyAuth
from api.client import HTTPClient
from api.config import ClientConfig, RetryConfig
from utils.helper import ConfigHelper
from utils.hooks import AllureReportHook, CompositeRequestHook
from utils.validations import ResponseTimeValidator, StatusValidator


@pytest.fixture(scope="session")
def client():
    config_helper = ConfigHelper()
    base_url = config_helper.get("base_url")
    retry = RetryConfig(**config_helper.get("retry", {}))
    validation = config_helper.get("validation", {})

    client_config = ClientConfig(base_url=base_url, retry=retry)
    hook = CompositeRequestHook(
        AllureReportHook(),
        StatusValidator(allowed_status=validation.get("allowed_status")),
        ResponseTimeValidator(default_max=validation.get("response_wait_timeout")),
    )
    with HTTPClient(config=client_config, hook=hook) as client:
        client.set_auth(APIKeyAuth(api_key=config_helper.get("api_key", "")))
        yield client


@pytest.fixture
def data(request) -> dict:
    """Indirect parametrize fixture that handles skip logic and processes other fields in allure report."""
    data = request.param
    if data.get("is_skip"):
        pytest.skip(reason=data.get("skip_reason", "Skipped by test data"))
    request.node.user_properties.append(("allure_description", data.get("description", "")))

    # Hide specific fields in allure report for cleaner report
    _HIDDEN = {"description", "is_skip", "skip_reason", "data"}
    for key, value in data.items():
        if key in _HIDDEN:
            continue
        if key == "expected":
            for expected_key, expected_value in value.items():
                allure.dynamic.parameter(f"expected.{expected_key}", expected_value)
        else:
            allure.dynamic.parameter(key, value)
    return data
