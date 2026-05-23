from typing import Optional

import requests

from api.endpoints import BaseAPI


class EndpointConst:
    COUNTRIES = "/countries"
    LEAGUES = "/leagues"
    TEAMS = "/teams"
    TEAM_STATISTICS = "/teams/statistics"
    TEAM_SEASONS = "/teams/seasons"
    TEAM_COUNTRIES = "/teams/countries"


class FootballAPI(BaseAPI):
    version = "v3"
    component = "football"

    def get_countries(
        self,
        name: Optional[str] = None,
        code: Optional[str] = None,
        search: Optional[str] = None,
        **kwargs,
    ) -> requests.Response:
        params = {"name": name, "code": code, "search": search}
        return self._get(EndpointConst.COUNTRIES, params=params, **kwargs)

    def get_leagues(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        country: Optional[str] = None,
        code: Optional[str] = None,
        season: Optional[int] = None,
        team: Optional[int] = None,
        type: Optional[str] = None,
        current: Optional[bool] = None,
        search: Optional[str] = None,
        **kwargs,
    ) -> requests.Response:
        params = {
            "id": id,
            "name": name,
            "country": country,
            "code": code,
            "season": season,
            "team": team,
            "type": type,
            "current": None if current is None else str(current).lower(),
            "search": search,
        }
        return self._get(EndpointConst.LEAGUES, params=params, **kwargs)

    def get_teams(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        league: Optional[int] = None,
        season: Optional[int] = None,
        country: Optional[str] = None,
        code: Optional[str] = None,
        venue: Optional[int] = None,
        search: Optional[str] = None,
        **kwargs,
    ) -> requests.Response:
        params = {
            "id": id,
            "name": name,
            "league": league,
            "season": season,
            "country": country,
            "code": code,
            "venue": venue,
            "search": search,
        }
        return self._get(EndpointConst.TEAMS, params=params, **kwargs)

    def get_team_statistics(
        self,
        league: int,
        season: int,
        team: int,
        date: Optional[str] = None,
        **kwargs,
    ) -> requests.Response:
        params = {
            "league": league,
            "season": season,
            "team": team,
            "date": date,
        }
        return self._get(EndpointConst.TEAM_STATISTICS, params=params, **kwargs)

    def get_team_seasons(
        self,
        team: int,
        **kwargs,
    ) -> requests.Response:
        params = {
            "team": team,
        }
        return self._get(EndpointConst.TEAM_SEASONS, params=params, **kwargs)

    def get_team_countries(
        self,
        **kwargs,
    ) -> requests.Response:
        return self._get(EndpointConst.TEAM_COUNTRIES, **kwargs)
