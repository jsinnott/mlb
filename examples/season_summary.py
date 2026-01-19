#!/usr/bin/env python3
"""Generate a CSV summary of a team's season results.

This sample script outputs a CSV file containing game-by-game results
for a team's season, including dates, opponents, scores, records, and
pitching decisions.

Usage:
    python season_summary.py [team_name] [--year YEAR] [--output FILE]

Examples:
    python season_summary.py "San Francisco Giants" --year 2025
    python season_summary.py "New York Yankees" --year 2025 --output yankees.csv
    python season_summary.py  # defaults to Giants, 2025, stdout
"""

import argparse
import csv
import sys
from datetime import datetime
from typing import TextIO

from mlb import MlbClient, Game, Team


def get_opponent(game: Game, team_id: int) -> Team:
    """Get the opponent team."""
    if game.home_team.id == team_id:
        return game.away_team
    return game.home_team


def get_location(game: Game, team_id: int) -> str:
    """Get 'Home' or 'Away' for the team."""
    if game.home_team.id == team_id:
        return "Home"
    return "Away"


def get_result(game: Game, team_id: int) -> str:
    """Get the result string (W/L and score)."""
    if game.is_tie:
        return f"T {game.home_team_score}-{game.away_team_score}"

    if game.winning_team and game.winning_team.id == team_id:
        return f"W {game.winning_team_score}-{game.losing_team_score}"
    else:
        return f"L {game.losing_team_score}-{game.winning_team_score}"


def get_team_record(game: Game, team_id: int) -> str:
    """Get the team's record after this game."""
    if game.home_team.id == team_id:
        return f"{game.home_team.record_wins}-{game.home_team.record_losses}"
    return f"{game.away_team.record_wins}-{game.away_team.record_losses}"


def get_opponent_record(game: Game, team_id: int) -> str:
    """Get the opponent's record after this game."""
    opponent = get_opponent(game, team_id)
    if game.home_team.id == opponent.id:
        return f"{game.home_team.record_wins}-{game.home_team.record_losses}"
    return f"{game.away_team.record_wins}-{game.away_team.record_losses}"


def write_csv(
    games: list[Game],
    team: Team,
    client: MlbClient,
    output: TextIO,
    include_preseason: bool = False,
) -> int:
    """Write game data to CSV.

    Args:
        games: List of completed games.
        team: The team to report on.
        client: MlbClient for fetching additional data.
        output: File-like object to write to.
        include_preseason: Whether to include preseason games.

    Returns:
        Number of games written.
    """
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "Date",
        "Day",
        "Location",
        "Opponent",
        "Result",
        "Team Record",
        "Opp Record",
        "Win Pitcher",
        "Lose Pitcher",
        "Save Pitcher",
        "Game Type",
    ])

    count = 0
    for game in games:
        # Filter by game type
        if game.game_type == "PS" and not include_preseason:
            continue

        # Get pitching decisions
        winner, loser, save = client.get_game_decisions(game.id)

        # Determine if our team's pitcher won or lost
        opponent = get_opponent(game, team.id)
        result = get_result(game, team.id)

        writer.writerow([
            game.date.strftime("%Y-%m-%d"),
            game.date.strftime("%a"),
            get_location(game, team.id),
            opponent.abbreviation,
            result,
            get_team_record(game, team.id),
            get_opponent_record(game, team.id),
            winner or "",
            loser or "",
            save or "",
            game.game_type,
        ])
        count += 1

        # Progress indicator to stderr
        if count % 10 == 0:
            print(f"Processed {count} games...", file=sys.stderr)

    return count


def main():
    parser = argparse.ArgumentParser(
        description="Generate a CSV summary of a team's season results."
    )
    parser.add_argument(
        "team",
        nargs="?",
        default="San Francisco Giants",
        help="Team name (default: San Francisco Giants)",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2025,
        help="Season year (default: 2025)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--preseason",
        action="store_true",
        help="Include preseason games",
    )
    args = parser.parse_args()

    client = MlbClient()

    try:
        team = client.get_team_by_name(args.team)
    except ValueError:
        print(f"Error: Team '{args.team}' not found.", file=sys.stderr)
        print("\nAvailable teams:", file=sys.stderr)
        for t in sorted(client.get_teams(), key=lambda x: x.name):
            print(f"  {t.name}", file=sys.stderr)
        return 1

    print(f"Fetching {args.year} season for {team.name}...", file=sys.stderr)

    # Get all games for the year
    start_date = datetime(args.year, 1, 1)
    end_date = datetime(args.year, 12, 31)

    all_games = team.get_games(
        start_date=start_date,
        end_date=end_date,
        include_preseason=args.preseason,
    )

    # Filter to completed games only
    completed_games = [g for g in all_games if g.is_completed]
    completed_games.sort(key=lambda g: g.date)

    print(f"Found {len(completed_games)} completed games.", file=sys.stderr)

    if not completed_games:
        print("No completed games found.", file=sys.stderr)
        return 0

    # Write output
    if args.output:
        with open(args.output, "w", newline="") as f:
            count = write_csv(completed_games, team, client, f, args.preseason)
        print(f"Wrote {count} games to {args.output}", file=sys.stderr)
    else:
        count = write_csv(completed_games, team, client, sys.stdout, args.preseason)
        print(f"Wrote {count} games.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    exit(main())
