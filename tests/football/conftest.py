import pytest
from api.endpoints.football import FootballAPI


@pytest.fixture(scope="class", autouse=True)
def api(request, client):
    request.cls.api = FootballAPI(client)
