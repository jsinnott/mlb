# MLB API Client

A Python library for accessing MLB game and team data from the MLB Stats API.

## Features

- Fetch teams, leagues, divisions, and games from the MLB Stats API
- Type-safe parsing using Pydantic models
- Convenient domain classes with navigation methods (e.g., `team.get_games()`)
- TTL-based caching to reduce API calls
- Filters to MLB-only data (excludes minor leagues)

## Installation

```bash
# Clone and install in development mode
git clone https://github.com/yourusername/mlb.git
cd mlb
uv venv venv
source venv/bin/activate
uv pip install -e .
```

## Quick Start

```python
from datetime import datetime
from mlb import MlbClient

# Create a client
client = MlbClient()

# Get a team
giants = client.get_team_by_name("San Francisco Giants")
print(f"{giants.name} play at {giants.venue_name}")
# San Francisco Giants play at Oracle Park

# Get the team's division and division rivals
division = giants.get_division()
print(f"Division: {division.name}")
for team in division.get_teams():
    print(f"  {team.name}")

# Get games for a date range
games = giants.get_games(
    start_date=datetime(2025, 4, 1),
    end_date=datetime(2025, 4, 30)
)

for game in games:
    if game.is_completed:
        result = "W" if game.winning_team.id == giants.id else "L"
        print(f"{game.date.strftime('%m/%d')}: {game.short_name} ({result})")
    else:
        print(f"{game.date.strftime('%m/%d')}: {game.short_name}")
```

## API Overview

### MlbClient

The main entry point for accessing MLB data.

```python
client = MlbClient()

# Teams
teams = client.get_teams()                              # All 30 MLB teams
team = client.get_team(137)                             # By ID
team = client.get_team_by_name("San Francisco Giants")  # By name

# Leagues
leagues = client.get_leagues()                          # AL and NL
league = client.get_league(104)                         # By ID (104 = NL)

# Divisions
divisions = client.get_divisions()                      # All 6 divisions
division = client.get_division_by_name("National League West")

# Games
games = client.get_games(
    start_date=datetime(2025, 4, 1),
    end_date=datetime(2025, 4, 30),
    include_preseason=False  # Exclude spring training
)

# Clear cached data
client.clear_cache()
```

### Domain Models

**Team** - MLB team with venue, league, and division info
```python
team.id                 # 137
team.name               # "San Francisco Giants"
team.abbreviation       # "SF"
team.venue_name         # "Oracle Park"
team.division_name      # "National League West"
team.get_games(...)     # Games for this team
team.get_division()     # Division object
team.get_league()       # League object
```

**Game** - Individual game with teams, scores, and status
```python
game.id                 # Unique game ID
game.date               # Game date
game.state              # "Final", "Scheduled", "In Progress"
game.home_team          # Team object
game.away_team          # Team object
game.home_team_score    # Score (None if not started)
game.away_team_score
game.winning_team       # Team object (None if not completed)
game.short_name         # "SF 5 @ LAD 3 F"
game.is_completed       # True/False
game.is_in_progress
game.is_future
```

**League** - American League or National League
```python
league.get_divisions()  # Divisions in this league
league.get_teams()      # Teams in this league
```

**Division** - One of six MLB divisions
```python
division.get_teams()    # Teams in this division
division.get_league()   # Parent league
```

## Caching

The client caches API responses to reduce calls. Default TTLs:

| Resource   | TTL        | Rationale                    |
|------------|------------|------------------------------|
| Teams      | 1 hour     | Rarely change                |
| Leagues    | 1 hour     | Rarely change                |
| Divisions  | 1 hour     | Rarely change                |
| Games      | 5 minutes  | Scores update during play    |

Configure TTLs when creating the client:

```python
client = MlbClient(
    cache_ttl_teams=7200,     # 2 hours
    cache_ttl_games=60,       # 1 minute for live tracking
)
```

## Examples

The `examples/` directory contains sample scripts:

**team_schedule.py** - Display recent and upcoming games for a team:

```bash
python examples/team_schedule.py "San Francisco Giants"
python examples/team_schedule.py "New York Yankees" --past 5 --future 10
python examples/team_schedule.py --preseason  # include spring training
```

Output:
```
San Francisco Giants Schedule
----------------------------------------
Date   Day    Opponent  Result    Record
----------------------------------------
09/26  Fri    COL       W 6-3     81-78
09/27  Sat    COL       W 4-3     82-78
09/28  Sun    COL       W 4-0     83-78
----------------------------------------
```

**season_summary.py** - Generate CSV of season-to-date results:

```bash
python examples/season_summary.py "San Francisco Giants" --year 2025
python examples/season_summary.py "Los Angeles Dodgers" --year 2025 -o dodgers.csv
```

Output (CSV):
```
Date,Day,Location,Opponent,Result,Team Record,Opp Record,Win Pitcher,Lose Pitcher,Save Pitcher,Game Type
2025-04-01,Tue,Away,HOU,W 3-1,4-1,2-3,Logan Webb,Hayden Wesneski,Ryan Walker,RS
2025-04-02,Wed,Away,HOU,W 6-3,5-1,2-4,Randy Rodríguez,Framber Valdez,Camilo Doval,RS
...
```

## Documentation

Build the full API documentation:

```bash
uv pip install -e ".[docs]"
sphinx-build -b html docs docs/_build/html
open docs/_build/html/index.html
```

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

## Requirements

- Python 3.11+
- pydantic >= 2.0
- cachetools
- python-dateutil
- requests
