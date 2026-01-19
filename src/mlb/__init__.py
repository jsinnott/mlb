"""MLB API client library for accessing game and team data.

This library provides a Python interface to the MLB Stats API, allowing you to
fetch information about teams, games, leagues, and divisions. Data is parsed
into typed Pydantic models and wrapped in convenient domain classes.

Basic Usage:
    >>> from mlb import MlbClient
    >>> client = MlbClient()
    >>> giants = client.get_team_by_name("San Francisco Giants")
    >>> print(giants.division_name)
    National League West

Fetching Games:
    >>> from datetime import datetime
    >>> games = giants.get_games(
    ...     start_date=datetime(2025, 4, 1),
    ...     end_date=datetime(2025, 4, 30)
    ... )
    >>> for game in games:
    ...     print(game.short_name)

The library caches API responses using TTL-based caching to reduce API calls.
Cache durations are configurable per resource type when creating the client.

Classes:
    MlbClient: Main client for accessing MLB API data.
    Team: Represents an MLB team with methods to fetch related data.
    Game: Represents a single game with score, teams, and status information.
    League: Represents a league (American League or National League).
    Division: Represents a division (e.g., NL West).
"""

from mlb.client import MlbClient
from mlb.models.domain import Team, Game, League, Division

__all__ = ["MlbClient", "Team", "Game", "League", "Division"]
__version__ = "0.1.0"
