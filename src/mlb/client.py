"""MLB API client for fetching team, game, and league data.

This module provides the MlbClient class, which is the main entry point
for accessing MLB Stats API data. The client handles:

- HTTP requests to the MLB Stats API
- Response parsing using Pydantic models
- TTL-based caching to reduce API calls
- Filtering to MLB-only data (excludes minor leagues)

Example:
    >>> from mlb import MlbClient
    >>> client = MlbClient()
    >>> teams = client.get_teams()
    >>> giants = client.get_team_by_name("San Francisco Giants")
"""

from datetime import datetime
from typing import Optional
import logging

import requests
from cachetools import TTLCache

from mlb import constants
from mlb.models.api import (
    ScheduleResponse,
    TeamsResponse,
    LeaguesResponse,
    DivisionsResponse,
)
from mlb.models.domain import Team, Game, League, Division


class MlbClient:
    """Client for accessing MLB API data.

    This client provides methods to fetch teams, leagues, divisions, and games
    from the MLB Stats API. Results are cached using TTL caches to reduce
    API calls while keeping data reasonably fresh.

    Example::

        client = MlbClient()
        giants = client.get_team_by_name("San Francisco Giants")
        games = giants.get_games(
            start_date=datetime(2025, 4, 1),
            end_date=datetime(2025, 4, 30)
        )
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        cache_ttl_teams: int = constants.CACHE_TTL_TEAMS,
        cache_ttl_leagues: int = constants.CACHE_TTL_LEAGUES,
        cache_ttl_divisions: int = constants.CACHE_TTL_DIVISIONS,
        cache_ttl_games: int = constants.CACHE_TTL_GAMES,
    ):
        """Initialize the MLB client.

        Args:
            logger: Optional logger instance for debug output.
            cache_ttl_teams: Cache TTL for teams data in seconds.
            cache_ttl_leagues: Cache TTL for leagues data in seconds.
            cache_ttl_divisions: Cache TTL for divisions data in seconds.
            cache_ttl_games: Cache TTL for games data in seconds.
        """
        self.logger = logger or logging.getLogger(__name__)

        # Initialize caches with configurable TTLs
        self._teams_cache: TTLCache = TTLCache(maxsize=50, ttl=cache_ttl_teams)
        self._leagues_cache: TTLCache = TTLCache(maxsize=10, ttl=cache_ttl_leagues)
        self._divisions_cache: TTLCache = TTLCache(maxsize=20, ttl=cache_ttl_divisions)
        self._games_cache: TTLCache = TTLCache(maxsize=100, ttl=cache_ttl_games)

    def _make_request(self, url: str) -> dict:
        """Make a GET request to the MLB API.

        Args:
            url: The API endpoint URL.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            requests.HTTPError: If the request fails.
        """
        self.logger.debug(f"GET {url}")
        response = requests.get(url, timeout=constants.REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    # Teams

    def get_teams(self) -> list[Team]:
        """Get all MLB teams.

        Returns:
            List of Team objects for all 30 MLB teams.
        """
        cache_key = "all_teams"
        if cache_key in self._teams_cache:
            return self._teams_cache[cache_key]

        data = self._make_request(constants.TEAMS_URL)
        response = TeamsResponse.model_validate(data)

        teams = [
            Team.from_api(t, client=self)
            for t in response.teams
            if t.league.id in constants.MLB_LEAGUE_IDS
        ]

        self._teams_cache[cache_key] = teams
        return teams

    def get_team(self, team_id: int) -> Team:
        """Get a team by ID.

        Args:
            team_id: The MLB team ID.

        Returns:
            Team object for the specified team.

        Raises:
            ValueError: If the team is not found.
        """
        for team in self.get_teams():
            if team.id == team_id:
                return team
        raise ValueError(f"Team with ID {team_id} not found")

    def get_team_by_name(self, team_name: str) -> Team:
        """Get a team by name.

        Args:
            team_name: The full team name (e.g., "San Francisco Giants").

        Returns:
            Team object for the specified team.

        Raises:
            ValueError: If the team is not found.
        """
        for team in self.get_teams():
            if team.name == team_name:
                return team
        raise ValueError(f"Team with name '{team_name}' not found")

    # Leagues

    def get_leagues(self) -> list[League]:
        """Get MLB leagues (American League and National League).

        Returns:
            List of League objects for AL and NL.
        """
        cache_key = "all_leagues"
        if cache_key in self._leagues_cache:
            return self._leagues_cache[cache_key]

        data = self._make_request(constants.LEAGUES_URL)
        # Filter to MLB leagues before parsing (other leagues have inconsistent schemas)
        mlb_leagues_data = [l for l in data["leagues"] if l["id"] in constants.MLB_LEAGUE_IDS]
        data["leagues"] = mlb_leagues_data
        response = LeaguesResponse.model_validate(data)

        leagues = [League.from_api(l, client=self) for l in response.leagues]

        self._leagues_cache[cache_key] = leagues
        return leagues

    def get_league(self, league_id: int) -> Optional[League]:
        """Get a league by ID.

        Args:
            league_id: The MLB league ID (103 for AL, 104 for NL).

        Returns:
            League object or None if not found.
        """
        for league in self.get_leagues():
            if league.id == league_id:
                return league
        return None

    def get_league_by_name(self, league_name: str) -> Optional[League]:
        """Get a league by name.

        Args:
            league_name: The league name (e.g., "American League").

        Returns:
            League object or None if not found.
        """
        for league in self.get_leagues():
            if league.name == league_name:
                return league
        return None

    # Divisions

    def get_divisions(self) -> list[Division]:
        """Get all MLB divisions.

        Returns:
            List of Division objects for all 6 MLB divisions.
        """
        cache_key = "all_divisions"
        if cache_key in self._divisions_cache:
            return self._divisions_cache[cache_key]

        data = self._make_request(constants.DIVISIONS_URL)
        response = DivisionsResponse.model_validate(data)

        divisions = [
            Division.from_api(d, client=self)
            for d in response.divisions
            if d.sport.id == constants.MLB_SPORT_ID
        ]

        self._divisions_cache[cache_key] = divisions
        return divisions

    def get_division(self, division_id: int) -> Optional[Division]:
        """Get a division by ID.

        Args:
            division_id: The MLB division ID.

        Returns:
            Division object or None if not found.
        """
        for division in self.get_divisions():
            if division.id == division_id:
                return division
        return None

    def get_division_by_name(self, division_name: str) -> Optional[Division]:
        """Get a division by name.

        Args:
            division_name: The division name (e.g., "National League West").

        Returns:
            Division object or None if not found.
        """
        for division in self.get_divisions():
            if division.name == division_name:
                return division
        return None

    # Games

    def get_games(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_preseason: bool = False,
    ) -> list[Game]:
        """Get games within a date range.

        Args:
            start_date: Start of date range (defaults to Jan 1 of current year).
            end_date: End of date range (defaults to Dec 31 of current year).
            include_preseason: Whether to include spring training games.

        Returns:
            List of Game objects within the date range.
        """
        now = datetime.now()
        if start_date is None:
            start_date = datetime(now.year, 1, 1)
        if end_date is None:
            end_date = datetime(now.year, 12, 31)

        # Cache key includes date range and preseason flag
        cache_key = f"games_{start_date.strftime(constants.DATE_FORMAT)}_{end_date.strftime(constants.DATE_FORMAT)}_{include_preseason}"
        if cache_key in self._games_cache:
            return self._games_cache[cache_key]

        # MLB API doesn't handle multi-year queries well, so query each year separately
        all_dates = []
        for year in range(start_date.year, end_date.year + 1):
            api_start = f"{year}-01-01"
            api_end = f"{year}-12-31"
            url = constants.GAMES_URL.format(start_date=api_start, end_date=api_end)
            data = self._make_request(url)
            response = ScheduleResponse.model_validate(data)
            all_dates.extend(response.dates)

        games = []
        for date_entry in all_dates:
            for api_game in date_entry.games:
                # Filter by date range
                game_date = datetime.strptime(api_game.official_date, constants.DATE_FORMAT)
                if game_date < start_date or game_date > end_date:
                    continue

                # Filter out preseason unless requested
                if api_game.game_type == constants.GAME_TYPE_SPRING and not include_preseason:
                    continue

                # Filter out exhibition games (college teams, etc.)
                if api_game.game_type == constants.GAME_TYPE_EXHIBITION:
                    continue

                try:
                    game = Game.from_api(api_game, client=self)
                    games.append(game)
                except ValueError as e:
                    # Skip games with teams not in MLB (e.g., college exhibition games)
                    self.logger.debug(f"Skipping game {api_game.game_pk}: {e}")
                    continue

        self._games_cache[cache_key] = games
        return games

    def clear_cache(self) -> None:
        """Clear all caches. Useful for forcing fresh data."""
        self._teams_cache.clear()
        self._leagues_cache.clear()
        self._divisions_cache.clear()
        self._games_cache.clear()
