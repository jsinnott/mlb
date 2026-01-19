"""Constants for MLB API access."""

BASE_URL = "http://statsapi.mlb.com"

# API endpoints
GAMES_URL = f"{BASE_URL}/api/v1/schedule/games/?sportId=1&startDate={{start_date}}&endDate={{end_date}}"
TEAMS_URL = f"{BASE_URL}/api/v1/teams?sportId=1"
TEAM_URL = f"{BASE_URL}/api/v1/teams/{{team_id}}"
LEAGUES_URL = f"{BASE_URL}/api/v1/leagues"
DIVISIONS_URL = f"{BASE_URL}/api/v1/divisions"

# MLB league IDs (American League and National League)
MLB_LEAGUE_IDS = [103, 104]
AL_LEAGUE_ID = 103
NL_LEAGUE_ID = 104

# MLB sport ID (filters out minor leagues)
MLB_SPORT_ID = 1

# Game states
GAME_STATES_COMPLETED = ["Completed Early", "Final"]
GAME_STATES_NO_WINNER = ["Cancelled", "Postponed"]
GAME_STATES_IN_PROGRESS = ["In Progress", "Pre-Game", "Suspended", "Warmup"]
GAME_STATES_FUTURE = ["Scheduled"]

# Game types
GAME_TYPE_SPRING = "S"
GAME_TYPE_REGULAR = "R"
GAME_TYPE_POSTSEASON = "P"
GAME_TYPE_EXHIBITION = "E"

# Date format used by MLB API
DATE_FORMAT = "%Y-%m-%d"

# Cache TTLs (in seconds)
CACHE_TTL_TEAMS = 3600      # 1 hour - teams rarely change
CACHE_TTL_LEAGUES = 3600    # 1 hour
CACHE_TTL_DIVISIONS = 3600  # 1 hour
CACHE_TTL_GAMES = 300       # 5 minutes - games can change during play

# HTTP request timeout (in seconds)
REQUEST_TIMEOUT = 30.0
