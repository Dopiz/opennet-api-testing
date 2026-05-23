import pytest
from api.endpoints.basketball import BasketballAPI


@pytest.fixture(scope="class", autouse=True)
def api(request, client):
    request.cls.api = BasketballAPI(client)
