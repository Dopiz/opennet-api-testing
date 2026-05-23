import pytest
from api.endpoints.football import FootballAPI

from utils.decorators import parametrize
from utils.helper import DataHelper

testdata = DataHelper().read("football/leagues")


@pytest.mark.football
class TestLeagues:
    api: FootballAPI

    @parametrize(testdata["test_get_leagues"])
    def test_get_leagues(self, data):
        resp = self.api.get_leagues(
            id=data.get("id"),
            code=data.get("code"),
            season=data.get("season"),
        ).json()

        assert not resp["errors"]
        assert resp["results"] >= data["expected"]["count"]
        leagues = [item["league"]["name"] for item in resp["response"]]
        for league in data["expected"]["leagues"]:
            assert league in leagues

    @parametrize(testdata["test_get_league"])
    def test_get_league(self, data):
        resp = self.api.get_leagues(
            id=data.get("id"),
            code=data.get("code"),
            season=data.get("season"),
        ).json()

        assert not resp["errors"]
        assert resp["results"] == data["expected"]["count"]
        league = resp["response"][0]
        assert league["league"]["name"] == data["expected"]["name"]
        assert league["country"]["name"] == data["expected"]["country"]
        assert league["seasons"][0]["start"] == data["expected"]["start"]
        assert league["seasons"][0]["end"] == data["expected"]["end"]
