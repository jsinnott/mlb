"""Domain models with business logic for MLB data.

These classes wrap the raw API data and provide convenient methods
for working with teams, games, leagues, and divisions. They are the
primary interface for users of this library.

The domain models are dataclasses that include:
- All relevant data from the API in a clean, Pythonic format
- Methods to navigate relationships (e.g., team.get_division())
- Computed properties for common queries (e.g., game.is_completed)

Each domain object maintains a reference to the MlbClient that created it,
enabling lazy loading of related data.
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
    """Represents an MLB league (American League or National League).

    Attributes:
        id: Unique MLB identifier for the league (103=AL, 104=NL).
        name: Full league name (e.g., "American League").
        abbreviation: Short form (e.g., "AL", "NL").
        name_short: Alternative short name (e.g., "American").
        num_teams: Number of teams in the league.
        num_games: Number of games in the regular season.
        season: The season year as a string.

    Example:
        >>> client = MlbClient()
        >>> al = client.get_league_by_name("American League")
        >>> print(f"{al.name} has {al.num_teams} teams")
        American League has 15 teams
    """

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
        """Create a League from API response data.

        Args:
            api_league: The parsed API response object.
            client: Optional client reference for fetching related data.

        Returns:
            A new League instance.
        """
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
        """Get all divisions in this league.

        Returns:
            List of Division objects belonging to this league.
            Returns empty list if no client is associated.
        """
        if not self._client:
            return []
        return [d for d in self._client.get_divisions() if d.league_id == self.id]

    def get_teams(self) -> list["Team"]:
        """Get all teams in this league.

        Returns:
            List of Team objects belonging to this league.
            Returns empty list if no client is associated.
        """
        if not self._client:
            return []
        return [t for t in self._client.get_teams() if t.league_id == self.id]

    def get_games(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_preseason: bool = False,
    ) -> list["Game"]:
        """Get all games involving teams from this league.

        Args:
            start_date: Start of date range (defaults to Jan 1 of current year).
            end_date: End of date range (defaults to Dec 31 of current year).
            include_preseason: Whether to include spring training games.

        Returns:
            List of Game objects where at least one team is from this league.
            Returns empty list if no client is associated.
        """
        if not self._client:
            return []
        all_games = self._client.get_games(start_date, end_date, include_preseason)
        return [g for g in all_games if g.home_team.league_id == self.id or g.away_team.league_id == self.id]


@dataclass
class Division:
    """Represents an MLB division (e.g., NL West, AL East).

    Attributes:
        id: Unique MLB identifier for the division.
        name: Full division name (e.g., "National League West").
        abbreviation: Short form (e.g., "NLW").
        name_short: Alternative short name (e.g., "NL West").
        league_id: ID of the parent league (103=AL, 104=NL).

    Example:
        >>> client = MlbClient()
        >>> nlw = client.get_division_by_name("National League West")
        >>> for team in nlw.get_teams():
        ...     print(team.name)
    """

    id: int
    name: str
    abbreviation: str
    name_short: str
    league_id: int
    _client: Optional["MlbClient"] = field(default=None, repr=False)
    _api_data: Optional[ApiDivision] = field(default=None, repr=False)

    @classmethod
    def from_api(cls, api_division: ApiDivision, client: Optional["MlbClient"] = None) -> "Division":
        """Create a Division from API response data.

        Args:
            api_division: The parsed API response object.
            client: Optional client reference for fetching related data.

        Returns:
            A new Division instance.
        """
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
        """Get the league this division belongs to.

        Returns:
            The parent League object, or None if not found or no client.
        """
        if not self._client:
            return None
        return self._client.get_league(self.league_id)

    def get_teams(self) -> list["Team"]:
        """Get all teams in this division.

        Returns:
            List of Team objects belonging to this division.
            Returns empty list if no client is associated.
        """
        if not self._client:
            return []
        return [t for t in self._client.get_teams() if t.division_id == self.id]

    def get_games(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_preseason: bool = False,
    ) -> list["Game"]:
        """Get all games involving teams from this division.

        Args:
            start_date: Start of date range (defaults to Jan 1 of current year).
            end_date: End of date range (defaults to Dec 31 of current year).
            include_preseason: Whether to include spring training games.

        Returns:
            List of Game objects where at least one team is from this division.
            Returns empty list if no client is associated.
        """
        if not self._client:
            return []
        all_games = self._client.get_games(start_date, end_date, include_preseason)
        return [g for g in all_games if g.home_team.division_id == self.id or g.away_team.division_id == self.id]


@dataclass
class Team:
    """Represents an MLB team.

    Attributes:
        id: Unique MLB identifier for the team (e.g., 137 for Giants).
        name: Full team name (e.g., "San Francisco Giants").
        abbreviation: Short code (e.g., "SF", "NYY").
        team_name: Team name without city (e.g., "Giants").
        location_name: City/location name (e.g., "San Francisco").
        venue_id: ID of the team's home venue.
        venue_name: Name of the home venue (e.g., "Oracle Park").
        league_id: ID of the team's league (103=AL, 104=NL).
        league_name: Name of the team's league.
        division_id: ID of the team's division (may be None).
        division_name: Name of the team's division (may be None).
        record_wins: Season wins (populated in game context).
        record_losses: Season losses (populated in game context).

    Example:
        >>> client = MlbClient()
        >>> giants = client.get_team_by_name("San Francisco Giants")
        >>> print(f"{giants.name} play at {giants.venue_name}")
        San Francisco Giants play at Oracle Park
    """

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
    record_wins: int = 0
    record_losses: int = 0
    _client: Optional["MlbClient"] = field(default=None, repr=False)
    _api_data: Optional[ApiTeam] = field(default=None, repr=False)

    @classmethod
    def from_api(cls, api_team: ApiTeam, client: Optional["MlbClient"] = None) -> "Team":
        """Create a Team from API response data.

        Args:
            api_team: The parsed API response object.
            client: Optional client reference for fetching related data.

        Returns:
            A new Team instance.
        """
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
        """Get the league this team belongs to.

        Returns:
            The team's League object, or None if not found or no client.
        """
        if not self._client:
            return None
        return self._client.get_league(self.league_id)

    def get_division(self) -> Optional["Division"]:
        """Get the division this team belongs to.

        Returns:
            The team's Division object, or None if not found or no client.
        """
        if not self._client or not self.division_id:
            return None
        return self._client.get_division(self.division_id)

    def get_games(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_preseason: bool = False,
    ) -> list["Game"]:
        """Get all games for this team within a date range.

        Args:
            start_date: Start of date range (defaults to Jan 1 of current year).
            end_date: End of date range (defaults to Dec 31 of current year).
            include_preseason: Whether to include spring training games.

        Returns:
            List of Game objects where this team is home or away.
            Returns empty list if no client is associated.
        """
        if not self._client:
            return []
        all_games = self._client.get_games(start_date, end_date, include_preseason)
        return [g for g in all_games if g.home_team.id == self.id or g.away_team.id == self.id]


@dataclass
class Game:
    """Represents an MLB game.

    Games can be in different states: scheduled (future), in progress, or
    completed. The available data varies by state - scores and winners are
    only available for completed or in-progress games.

    Attributes:
        id: Unique game identifier (gamePk).
        date: The official date of the game (local date, no time).
        start_time: Scheduled start time (UTC datetime).
        game_type: Type code - "RS" (regular), "PS" (preseason), "POST" (playoff).
        state: Detailed state (e.g., "Final", "Scheduled", "In Progress").
        venue_id: ID of the venue where the game is played.
        venue_name: Name of the venue.
        home_team: The home Team object (includes record at game time).
        away_team: The away Team object (includes record at game time).
        home_team_score: Home team's score (None if game not started).
        away_team_score: Away team's score (None if game not started).
        winning_team: The winning Team (None if not completed or tie).
        winning_team_score: Winner's score (None if not completed).
        losing_team: The losing Team (None if not completed or tie).
        losing_team_score: Loser's score (None if not completed).
        is_tie: True if the game ended in a tie.
        name: Display name (e.g., "Giants 5 at Dodgers 3 F").
        short_name: Short display name (e.g., "SF 5 @ LAD 3 F").
        series_description: Description of the series (e.g., "Regular Season").
        series_game_number: Game number within the series.
        games_in_series: Total games in the series.
        home_probable_pitcher: Name of the home team's probable starting pitcher (if announced).
        home_probable_pitcher_id: MLB person ID of the home probable pitcher (if announced).
        away_probable_pitcher: Name of the away team's probable starting pitcher (if announced).
        away_probable_pitcher_id: MLB person ID of the away probable pitcher (if announced).

    Example:
        >>> client = MlbClient()
        >>> giants = client.get_team_by_name("San Francisco Giants")
        >>> games = giants.get_games(start_date=datetime(2025, 4, 1), end_date=datetime(2025, 4, 7))
        >>> for game in games:
        ...     if game.is_completed:
        ...         result = "W" if game.winning_team.id == giants.id else "L"
        ...         print(f"{game.date.strftime('%m/%d')}: {game.short_name} ({result})")
    """

    id: int
    date: datetime
    start_time: datetime
    game_type: str
    state: str
    venue_id: int
    venue_name: str
    home_team: Team
    away_team: Team
    home_team_score: Optional[int] = None
    away_team_score: Optional[int] = None
    winning_team: Optional[Team] = None
    winning_team_score: Optional[int] = None
    losing_team: Optional[Team] = None
    losing_team_score: Optional[int] = None
    is_tie: bool = False
    name: str = ""
    short_name: str = ""
    series_description: str = ""
    series_game_number: int = 1
    games_in_series: int = 1
    home_probable_pitcher: Optional[str] = None
    home_probable_pitcher_id: Optional[int] = None
    away_probable_pitcher: Optional[str] = None
    away_probable_pitcher_id: Optional[int] = None
    _client: Optional["MlbClient"] = field(default=None, repr=False)
    _api_data: Optional[ApiGame] = field(default=None, repr=False)

    @classmethod
    def from_api(cls, api_game: ApiGame, client: "MlbClient") -> "Game":
        """Create a Game from API response data.

        This method fetches team information and constructs a complete Game
        object with all relevant data populated based on the game's state.

        Args:
            api_game: The parsed API response object.
            client: Client reference for fetching team data.

        Returns:
            A new Game instance.

        Raises:
            ValueError: If a team referenced in the game is not found.
        """
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

        # Extract probable pitcher names if announced
        home_pitcher = api_game.teams.home.probable_pitcher
        away_pitcher = api_game.teams.away.probable_pitcher

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
            home_probable_pitcher=home_pitcher.full_name if home_pitcher else None,
            home_probable_pitcher_id=home_pitcher.id if home_pitcher else None,
            away_probable_pitcher=away_pitcher.full_name if away_pitcher else None,
            away_probable_pitcher_id=away_pitcher.id if away_pitcher else None,
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
        """Check if the game has finished.

        Returns:
            True if the game state indicates completion (Final, Completed Early).
        """
        return self.state in constants.GAME_STATES_COMPLETED

    @property
    def is_in_progress(self) -> bool:
        """Check if the game is currently being played.

        Returns:
            True if the game is in progress, warmup, or suspended.
        """
        return self.state in constants.GAME_STATES_IN_PROGRESS

    @property
    def is_future(self) -> bool:
        """Check if the game is scheduled for the future.

        Returns:
            True if the game has not yet started.
        """
        return self.state in constants.GAME_STATES_FUTURE
