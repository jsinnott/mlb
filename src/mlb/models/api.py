"""Pydantic models for MLB API responses.

These models directly represent the JSON structure returned by MLB APIs.
They are intentionally kept close to the API schema for accurate parsing.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# Nested/shared models

class ApiLink(BaseModel):
    """A link reference in API responses."""
    id: int
    link: str
    name: Optional[str] = None


class ApiVenue(BaseModel):
    """Venue information."""
    id: int
    name: str
    link: str


class ApiLeagueRef(BaseModel):
    """League reference within other objects."""
    id: int
    link: str
    name: Optional[str] = None


class ApiDivisionRef(BaseModel):
    """Division reference within other objects."""
    id: int
    name: str
    link: str


class ApiSportRef(BaseModel):
    """Sport reference within other objects."""
    id: int
    link: str
    name: Optional[str] = None


class ApiSpringLeague(BaseModel):
    """Spring training league reference."""
    id: int
    name: str
    link: str
    abbreviation: str


# Team models

class ApiTeam(BaseModel):
    """Team data from the teams API."""
    id: int
    name: str
    link: str
    season: int
    venue: ApiVenue
    team_code: str = Field(alias="teamCode")
    file_code: str = Field(alias="fileCode")
    abbreviation: str
    team_name: str = Field(alias="teamName")
    location_name: str = Field(alias="locationName")
    first_year_of_play: str = Field(alias="firstYearOfPlay")
    league: ApiLeagueRef
    division: Optional[ApiDivisionRef] = None
    sport: ApiSportRef
    short_name: str = Field(alias="shortName")
    franchise_name: str = Field(alias="franchiseName")
    club_name: str = Field(alias="clubName")
    active: bool
    spring_league: Optional[ApiSpringLeague] = Field(default=None, alias="springLeague")
    all_star_status: str = Field(alias="allStarStatus")
    spring_venue: Optional[ApiLink] = Field(default=None, alias="springVenue")

    model_config = {"populate_by_name": True}


class TeamsResponse(BaseModel):
    """Response from the teams API."""
    copyright: str
    teams: list[ApiTeam]


# League models

class ApiSeasonDateInfo(BaseModel):
    """Season date information for a league."""
    season_id: str = Field(alias="seasonId")
    pre_season_start_date: str = Field(alias="preSeasonStartDate")
    pre_season_end_date: str = Field(alias="preSeasonEndDate")
    season_start_date: str = Field(alias="seasonStartDate")
    spring_start_date: str = Field(alias="springStartDate")
    spring_end_date: str = Field(alias="springEndDate")
    regular_season_start_date: str = Field(alias="regularSeasonStartDate")
    last_date_1st_half: str = Field(alias="lastDate1stHalf")
    all_star_date: str = Field(alias="allStarDate")
    first_date_2nd_half: str = Field(alias="firstDate2ndHalf")
    regular_season_end_date: str = Field(alias="regularSeasonEndDate")
    post_season_start_date: str = Field(alias="postSeasonStartDate")
    post_season_end_date: str = Field(alias="postSeasonEndDate")
    season_end_date: str = Field(alias="seasonEndDate")
    offseason_start_date: str = Field(alias="offseasonStartDate")
    off_season_end_date: str = Field(alias="offSeasonEndDate")
    season_level_gameday_type: str = Field(alias="seasonLevelGamedayType")
    game_level_gameday_type: str = Field(alias="gameLevelGamedayType")
    qualifier_plate_appearances: float = Field(alias="qualifierPlateAppearances")
    qualifier_outs_pitched: float = Field(alias="qualifierOutsPitched")

    model_config = {"populate_by_name": True}


class ApiLeague(BaseModel):
    """League data from the leagues API."""
    id: int
    name: str
    link: str
    abbreviation: str
    name_short: str = Field(alias="nameShort")
    season_state: str = Field(alias="seasonState")
    has_wild_card: bool = Field(alias="hasWildCard")
    has_split_season: bool = Field(alias="hasSplitSeason")
    num_games: int = Field(alias="numGames")
    has_playoff_points: bool = Field(alias="hasPlayoffPoints")
    num_teams: int = Field(alias="numTeams")
    num_wildcard_teams: int = Field(alias="numWildcardTeams")
    season_date_info: ApiSeasonDateInfo = Field(alias="seasonDateInfo")
    season: str
    org_code: str = Field(alias="orgCode")
    conferences_in_use: bool = Field(alias="conferencesInUse")
    divisions_in_use: bool = Field(alias="divisionsInUse")
    sport: ApiSportRef
    sort_order: int = Field(alias="sortOrder")
    active: bool

    model_config = {"populate_by_name": True}


class LeaguesResponse(BaseModel):
    """Response from the leagues API."""
    copyright: str
    leagues: list[ApiLeague]


# Division models

class ApiDivision(BaseModel):
    """Division data from the divisions API."""
    id: int
    name: str
    season: str
    name_short: str = Field(alias="nameShort")
    link: str
    abbreviation: str
    league: ApiLeagueRef
    sport: ApiSportRef
    has_wildcard: bool = Field(alias="hasWildcard")
    sort_order: int = Field(alias="sortOrder")
    num_playoff_teams: Optional[int] = Field(default=None, alias="numPlayoffTeams")
    active: bool

    model_config = {"populate_by_name": True}


class DivisionsResponse(BaseModel):
    """Response from the divisions API."""
    copyright: str
    divisions: list[ApiDivision]


# Game/Schedule models

class ApiGameStatus(BaseModel):
    """Game status information."""
    abstract_game_state: str = Field(alias="abstractGameState")
    coded_game_state: str = Field(alias="codedGameState")
    detailed_state: str = Field(alias="detailedState")
    status_code: str = Field(alias="statusCode")
    start_time_tbd: bool = Field(alias="startTimeTBD")
    abstract_game_code: str = Field(alias="abstractGameCode")

    model_config = {"populate_by_name": True}


class ApiTeamRef(BaseModel):
    """Team reference within game data."""
    id: int
    name: str
    link: str


class ApiLeagueRecord(BaseModel):
    """Team's league record."""
    wins: int
    losses: int
    pct: str


class ApiProbablePitcher(BaseModel):
    """Probable pitcher for a scheduled game."""
    id: int
    full_name: str = Field(alias="fullName")
    link: str

    model_config = {"populate_by_name": True}


class ApiGameTeam(BaseModel):
    """Team data within a game."""
    team: ApiTeamRef
    league_record: ApiLeagueRecord = Field(alias="leagueRecord")
    score: Optional[int] = None
    is_winner: Optional[bool] = Field(default=None, alias="isWinner")
    split_squad: bool = Field(alias="splitSquad")
    series_number: Optional[int] = Field(default=None, alias="seriesNumber")
    probable_pitcher: Optional[ApiProbablePitcher] = Field(default=None, alias="probablePitcher")

    model_config = {"populate_by_name": True}


class ApiGameTeams(BaseModel):
    """Home and away teams for a game."""
    away: ApiGameTeam
    home: ApiGameTeam


class ApiGameContent(BaseModel):
    """Game content link."""
    link: str


class ApiGame(BaseModel):
    """Game data from the schedule API."""
    game_pk: int = Field(alias="gamePk")
    game_guid: str = Field(alias="gameGuid")
    link: str
    game_type: str = Field(alias="gameType")
    season: str
    game_date: datetime = Field(alias="gameDate")
    official_date: str = Field(alias="officialDate")
    status: ApiGameStatus
    teams: ApiGameTeams
    venue: ApiVenue
    content: ApiGameContent
    is_tie: Optional[bool] = Field(default=None, alias="isTie")
    game_number: int = Field(alias="gameNumber")
    public_facing: bool = Field(alias="publicFacing")
    double_header: str = Field(alias="doubleHeader")
    gameday_type: str = Field(alias="gamedayType")
    tiebreaker: str
    calendar_event_id: str = Field(alias="calendarEventID")
    season_display: str = Field(alias="seasonDisplay")
    day_night: str = Field(alias="dayNight")
    description: Optional[str] = None
    scheduled_innings: int = Field(alias="scheduledInnings")
    reverse_home_away_status: bool = Field(alias="reverseHomeAwayStatus")
    inning_break_length: int = Field(alias="inningBreakLength")
    games_in_series: Optional[int] = Field(default=None, alias="gamesInSeries")
    series_game_number: Optional[int] = Field(default=None, alias="seriesGameNumber")
    series_description: str = Field(alias="seriesDescription")
    record_source: str = Field(alias="recordSource")
    if_necessary: str = Field(alias="ifNecessary")
    if_necessary_description: str = Field(alias="ifNecessaryDescription")

    model_config = {"populate_by_name": True}


class ApiScheduleDate(BaseModel):
    """A single date in the schedule response."""
    date: str
    total_items: int = Field(alias="totalItems")
    total_events: int = Field(alias="totalEvents")
    total_games: int = Field(alias="totalGames")
    total_games_in_progress: int = Field(alias="totalGamesInProgress")
    games: list[ApiGame]
    events: list = []

    model_config = {"populate_by_name": True}


class ScheduleResponse(BaseModel):
    """Response from the schedule/games API."""
    copyright: str
    total_items: int = Field(alias="totalItems")
    total_events: int = Field(alias="totalEvents")
    total_games: int = Field(alias="totalGames")
    total_games_in_progress: int = Field(alias="totalGamesInProgress")
    dates: list[ApiScheduleDate]

    model_config = {"populate_by_name": True}


# Game detail models (from /game/{id}/feed/live endpoint)

class ApiPitcher(BaseModel):
    """Pitcher information in game decisions."""
    id: int
    full_name: str = Field(alias="fullName")
    link: str

    model_config = {"populate_by_name": True}


class ApiDecisions(BaseModel):
    """Pitching decisions for a completed game."""
    winner: Optional[ApiPitcher] = None
    loser: Optional[ApiPitcher] = None
    save: Optional[ApiPitcher] = None


class ApiLiveData(BaseModel):
    """Live data section of game feed response."""
    decisions: Optional[ApiDecisions] = None

    model_config = {"populate_by_name": True}


class GameFeedResponse(BaseModel):
    """Response from the game feed API (/game/{id}/feed/live)."""
    copyright: str
    game_pk: int = Field(alias="gamePk")
    link: str
    live_data: ApiLiveData = Field(alias="liveData")

    model_config = {"populate_by_name": True}


# Person/stats models (from /people/{id} endpoint)

class ApiPitchingStats(BaseModel):
    """Season pitching statistics."""
    wins: int = 0
    losses: int = 0
    era: str = "-.--"

    model_config = {"populate_by_name": True}


class ApiStatSplit(BaseModel):
    """A single stat split (e.g., one season)."""
    season: str
    stat: ApiPitchingStats

    model_config = {"populate_by_name": True}


class ApiStatGroup(BaseModel):
    """A group of stat splits (e.g., season pitching stats)."""
    splits: list[ApiStatSplit] = []

    model_config = {"populate_by_name": True}


class ApiPerson(BaseModel):
    """Person data from the people API."""
    id: int
    full_name: str = Field(alias="fullName")
    stats: list[ApiStatGroup] = []

    model_config = {"populate_by_name": True}


class PeopleResponse(BaseModel):
    """Response from the people API."""
    copyright: str
    people: list[ApiPerson]

    model_config = {"populate_by_name": True}
