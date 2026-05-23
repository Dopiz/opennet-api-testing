from typing import Optional

import requests

from api.endpoints import BaseAPI


class EndpointConst:
    COUNTRIES = "/countries"
    LEAGUES = "/leagues"
    TEAMS = "/teams"
    GAMES = "/games"
    GAMES_STATISTICS_PLAYERS = "/games/statistics/players"


class BasketballAPI(BaseAPI):
    version = "v1"
    component = "basketball"

    def get_countries(
        self,
        name: Optional[str] = None,
        code: Optional[str] = None,
        search: Optional[str] = None,
        **kwargs,
    ) -> requests.Response:
        params = {
            "name": name,
            "code": code,
            "search": search,
        }
        return self._get(EndpointConst.COUNTRIES, params=params, **kwargs)

    def get_leagues(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        country: Optional[str] = None,
        code: Optional[str] = None,
        season: Optional[str] = None,
        team: Optional[int] = None,
        type: Optional[str] = None,
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
            "search": search,
        }
        return self._get(EndpointConst.LEAGUES, params=params, **kwargs)

    def get_teams(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        league: Optional[int] = None,
        season: Optional[str] = None,
        country: Optional[str] = None,
        code: Optional[str] = None,
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
            "search": search,
        }
        return self._get(EndpointConst.TEAMS, params=params, **kwargs)

    def get_games(
        self,
        id: Optional[int] = None,
        date: Optional[str] = None,
        league: Optional[int] = None,
        season: Optional[str] = None,
        team: Optional[int] = None,
        timezone: Optional[str] = None,
        h2h: Optional[str] = None,
        live: Optional[str] = None,
        **kwargs,
    ) -> requests.Response:
        params = {
            "id": id,
            "date": date,
            "league": league,
            "season": season,
            "team": team,
            "timezone": timezone,
            "h2h": h2h,
            "live": live,
        }
        return self._get(EndpointConst.GAMES, params=params, **kwargs)

    def get_games_statistics_players(
        self,
        id: int,
        team: Optional[int] = None,
        **kwargs,
    ) -> requests.Response:
        params = {
            "id": id,
            "team": team,
        }
        return self._get(EndpointConst.GAMES_STATISTICS_PLAYERS, params=params, **kwargs)
