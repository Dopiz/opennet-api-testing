import pytest
from api.endpoints.football import FootballAPI

from utils.decorators import parametrize
from utils.helper import DataHelper

testdata = DataHelper().read("football/teams")


@pytest.mark.football
class TestTeams:
    api: FootballAPI

    @parametrize(testdata["test_get_teams"])
    def test_get_teams(self, data):
        resp = self.api.get_teams(
            league=data.get("league"),
            season=data.get("season"),
            country=data.get("country"),
            code=data.get("code"),
        ).json()

        if data["expected"]["success"]:
            assert not resp["errors"]
            assert resp["results"] == data["expected"]["count"]
            teams = [team["team"]["name"] for team in resp["response"]]
            assert all([team in teams for team in data["expected"]["teams"]])
        else:
            assert resp["errors"]

    @parametrize(testdata["test_get_team_statistics"])
    def test_get_team_statistics(self, data):
        resp = self.api.get_team_statistics(
            league=data["league"],
            season=data["season"],
            team=data["team"],
        ).json()

        assert not resp["errors"]
        assert resp["response"]["team"]["name"] == data["expected"]["name"]
        assert resp["response"]["form"] == data["expected"]["form"]
