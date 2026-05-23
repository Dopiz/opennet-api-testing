import pytest
from api.endpoints.football import FootballAPI

from utils.decorators import parametrize
from utils.helper import DataHelper

testdata = DataHelper().read("football/countries")


@pytest.mark.football
class TestCountries:
    api: FootballAPI

    @parametrize(testdata["test_get_countries"])
    def test_get_countries(self, data):
        resp = self.api.get_countries().json()

        assert not resp["errors"]
        assert resp["results"] >= data["expected"]["count"]
        country_codes = [country["code"] for country in resp["response"]]
        assert all(code in country_codes for code in data["expected"]["code"])

    @parametrize(testdata["test_get_country"])
    def test_get_country(self, data):
        resp = self.api.get_countries(
            name=data.get("name"),
            code=data.get("code"),
            search=data.get("search"),
        ).json()

        if data["expected"]["success"]:
            assert not resp["errors"]
            country = resp["response"][0]
            assert country["code"] == data["expected"]["code"]
            assert country["name"] == data["expected"]["name"]
            assert country["flag"] == data["expected"]["flag"]
        else:
            assert resp["errors"]
            assert resp["errors"]["search"] == data["expected"]["message"]
