"""Domain models with business logic for MLB data.

These classes wrap the raw API data and provide convenient methods
for working with teams, games, leagues, and divisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from mlb.models.api import ApiGame, ApiTeam, ApiLeague, ApiDivision
from mlb import constants

if TYPE_CHECKING:
    from mlb.client import MlbClient


@dataclass
class League:
    """Represents an MLB league (American League or National League)."""

    id: int
    name: str
    abbreviation: str
    name_short: str
    num_teams: int
    num_games: int
    season: str
    _client: Optional["MlbClient"] = field(default=None, repr=False)
    _api_data: Optional[ApiLeague] = field(default=None, repr=False)

    @classmethod
    def from_api(cls, api_league: ApiLeague, client: Optional["MlbClient"] = None) -> "League":
        """Create a League from API data."""
        return cls(
            id=api_league.id,
            name=api_league.name,
            abbreviation=api_league.abbreviation,
            name_short=api_league.name_short,
            num_teams=api_league.num_teams,
            num_games=api_league.num_games,
            season=api_league.season,
            _client=client,
            _api_data=api_league,
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

    def get_divisions(self) -> list["Division"]:
        """Get all divisions in this league."""
        if not self._client:
            return []
        return [d for d in self._client.get_divisions() if d.league_id == self.id]

    def get_teams(self) -> list["Team"]:
        """Get all teams in this league."""
        if not self._client:
            return []
        return [t for t in self._client.get_teams() if t.league_id == self.id]

    def get_games(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_preseason: bool = False,
    ) -> list["Game"]:
        """Get all games involving teams from this league."""
        if not self._client:
            return []
        all_games = self._client.get_games(start_date, end_date, include_preseason)
        return [g for g in all_games if g.home_team.league_id == self.id or g.away_team.league_id == self.id]


@dataclass
class Division:
    """Represents an MLB division."""

    id: int
    name: str
    abbreviation: str
    name_short: str
    league_id: int
    _client: Optional["MlbClient"] = field(default=None, repr=False)
    _api_data: Optional[ApiDivision] = field(default=None, repr=False)

    @classmethod
    def from_api(cls, api_division: ApiDivision, client: Optional["MlbClient"] = None) -> "Division":
        """Create a Division from API data."""
        return cls(
            id=api_division.id,
            name=api_division.name,
            abbreviation=api_division.abbreviation,
            name_short=api_division.name_short,
            league_id=api_division.league.id,
            _client=client,
            _api_data=api_division,
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

    def get_league(self) -> Optional["League"]:
        """Get the league this division belongs to."""
        if not self._client:
            return None
        return self._client.get_league(self.league_id)

    def get_teams(self) -> list["Team"]:
        """Get all teams in this division."""
        if not self._client:
            return []
        return [t for t in self._client.get_teams() if t.division_id == self.id]

    def get_games(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_preseason: bool = False,
    ) -> list["Game"]:
        """Get all games involving teams from this division."""
        if not self._client:
            return []
        all_games = self._client.get_games(start_date, end_date, include_preseason)
        return [g for g in all_games if g.home_team.division_id == self.id or g.away_team.division_id == self.id]


@dataclass
class Team:
    """Represents an MLB team."""

    id: int
    name: str
    abbreviation: str
    team_name: str
    location_name: str
    venue_id: int
    venue_name: str
    league_id: int
    league_name: str
    division_id: Optional[int]
    division_name: Optional[str]
    # Record (set when team appears in game context)
    record_wins: int = 0
    record_losses: int = 0
    _client: Optional["MlbClient"] = field(default=None, repr=False)
    _api_data: Optional[ApiTeam] = field(default=None, repr=False)

    @classmethod
    def from_api(cls, api_team: ApiTeam, client: Optional["MlbClient"] = None) -> "Team":
        """Create a Team from API data."""
        return cls(
            id=api_team.id,
            name=api_team.name,
            abbreviation=api_team.abbreviation,
            team_name=api_team.team_name,
            location_name=api_team.location_name,
            venue_id=api_team.venue.id,
            venue_name=api_team.venue.name,
            league_id=api_team.league.id,
            league_name=api_team.league.name or "",
            division_id=api_team.division.id if api_team.division else None,
            division_name=api_team.division.name if api_team.division else None,
            _client=client,
            _api_data=api_team,
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

    def get_league(self) -> Optional["League"]:
        """Get the league this team belongs to."""
        if not self._client:
            return None
        return self._client.get_league(self.league_id)

    def get_division(self) -> Optional["Division"]:
        """Get the division this team belongs to."""
        if not self._client or not self.division_id:
            return None
        return self._client.get_division(self.division_id)

    def get_games(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_preseason: bool = False,
    ) -> list["Game"]:
        """Get all games for this team."""
        if not self._client:
            return []
        all_games = self._client.get_games(start_date, end_date, include_preseason)
        return [g for g in all_games if g.home_team.id == self.id or g.away_team.id == self.id]


@dataclass
class Game:
    """Represents an MLB game."""

    id: int
    date: datetime
    start_time: datetime
    game_type: str
    state: str
    venue_id: int
    venue_name: str
    home_team: Team
    away_team: Team
    # Scores (only present for completed/in-progress games)
    home_team_score: Optional[int] = None
    away_team_score: Optional[int] = None
    # Winner/loser (only for completed games)
    winning_team: Optional[Team] = None
    winning_team_score: Optional[int] = None
    losing_team: Optional[Team] = None
    losing_team_score: Optional[int] = None
    is_tie: bool = False
    # Display names
    name: str = ""
    short_name: str = ""
    # Series info
    series_description: str = ""
    series_game_number: int = 1
    games_in_series: int = 1
    _client: Optional["MlbClient"] = field(default=None, repr=False)
    _api_data: Optional[ApiGame] = field(default=None, repr=False)

    @classmethod
    def from_api(cls, api_game: ApiGame, client: "MlbClient") -> "Game":
        """Create a Game from API data."""
        # Get team objects
        home_team = client.get_team(api_game.teams.home.team.id)
        away_team = client.get_team(api_game.teams.away.team.id)

        # Copy teams and update records from game context
        home_team = Team(
            id=home_team.id,
            name=home_team.name,
            abbreviation=home_team.abbreviation,
            team_name=home_team.team_name,
            location_name=home_team.location_name,
            venue_id=home_team.venue_id,
            venue_name=home_team.venue_name,
            league_id=home_team.league_id,
            league_name=home_team.league_name,
            division_id=home_team.division_id,
            division_name=home_team.division_name,
            record_wins=api_game.teams.home.league_record.wins,
            record_losses=api_game.teams.home.league_record.losses,
            _client=client,
        )
        away_team = Team(
            id=away_team.id,
            name=away_team.name,
            abbreviation=away_team.abbreviation,
            team_name=away_team.team_name,
            location_name=away_team.location_name,
            venue_id=away_team.venue_id,
            venue_name=away_team.venue_name,
            league_id=away_team.league_id,
            league_name=away_team.league_name,
            division_id=away_team.division_id,
            division_name=away_team.division_name,
            record_wins=api_game.teams.away.league_record.wins,
            record_losses=api_game.teams.away.league_record.losses,
            _client=client,
        )

        state = api_game.status.detailed_state
        game_type = "RS"  # Regular season
        if api_game.game_type == constants.GAME_TYPE_SPRING:
            game_type = "PS"  # Preseason
        elif api_game.game_type == constants.GAME_TYPE_POSTSEASON:
            game_type = "POST"

        game = cls(
            id=api_game.game_pk,
            date=datetime.strptime(api_game.official_date, constants.DATE_FORMAT),
            start_time=api_game.game_date,
            game_type=game_type,
            state=state,
            venue_id=api_game.venue.id,
            venue_name=api_game.venue.name,
            home_team=home_team,
            away_team=away_team,
            series_description=api_game.series_description,
            series_game_number=api_game.series_game_number or 1,
            games_in_series=api_game.games_in_series or 1,
            _client=client,
            _api_data=api_game,
        )

        # Set scores and winner for completed games
        if state in constants.GAME_STATES_COMPLETED:
            game.home_team_score = api_game.teams.home.score
            game.away_team_score = api_game.teams.away.score
            game.is_tie = api_game.is_tie or False

            if api_game.teams.home.is_winner:
                game.winning_team = home_team
                game.winning_team_score = game.home_team_score
                game.losing_team = away_team
                game.losing_team_score = game.away_team_score
            elif api_game.teams.away.is_winner:
                game.winning_team = away_team
                game.winning_team_score = game.away_team_score
                game.losing_team = home_team
                game.losing_team_score = game.home_team_score

            game.name = f"{away_team.name} {game.away_team_score} at {home_team.name} {game.home_team_score} F"
            game.short_name = f"{away_team.abbreviation} {game.away_team_score} @ {home_team.abbreviation} {game.home_team_score} F"
        elif state in constants.GAME_STATES_IN_PROGRESS:
            game.home_team_score = api_game.teams.home.score
            game.away_team_score = api_game.teams.away.score
            game.name = f"{away_team.name} {game.away_team_score} at {home_team.name} {game.home_team_score} ({state})"
            game.short_name = f"{away_team.abbreviation} {game.away_team_score} @ {home_team.abbreviation} {game.home_team_score} ({state})"
        else:
            game.name = f"{away_team.name} at {home_team.name} ({state})"
            game.short_name = f"{away_team.abbreviation} @ {home_team.abbreviation} ({state})"

        return game

    def __str__(self) -> str:
        return self.name

    @property
    def is_completed(self) -> bool:
        """Check if the game is completed."""
        return self.state in constants.GAME_STATES_COMPLETED

    @property
    def is_in_progress(self) -> bool:
        """Check if the game is in progress."""
        return self.state in constants.GAME_STATES_IN_PROGRESS

    @property
    def is_future(self) -> bool:
        """Check if the game is scheduled for the future."""
        return self.state in constants.GAME_STATES_FUTURE
