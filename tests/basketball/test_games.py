import pytest
from api.endpoints.basketball import BasketballAPI

from utils.decorators import parametrize
from utils.helper import DataHelper

testdata = DataHelper().read("basketball/games")


@pytest.mark.basketball
class TestGames:
    api: BasketballAPI

    @parametrize(testdata["test_get_games"])
    def test_get_games(self, data):
        resp = self.api.get_games(
            league=data.get("league"),
            season=data.get("season"),
            date=data.get("date"),
        ).json()

        if data["expected"]["success"]:
            assert not resp["errors"]
            assert resp["results"] == data["expected"]["results"]
        else:
            assert resp["errors"]
            assert resp["errors"]["plan"] == data["expected"]["message"]

    @parametrize(testdata["test_get_games_statistics_players"])
    def test_get_games_statistics_players(self, data):
        resp = self.api.get_games_statistics_players(id=data["id"]).json()

        assert not resp["errors"]
        for player in resp["response"]:
            if player["player"]["name"] == data["expected"]["name"]:
                assert player["points"] == data["expected"]["points"]
                assert player["assists"] == data["expected"]["assists"]
                assert player["rebounds"]["total"] == data["expected"]["rebounds"]
                break
        else:
            pytest.fail(f"{data['expected']['name']} was expected to be included in the statistics")
