#!/usr/bin/env python3
"""Display recent and upcoming games for an MLB team.

This sample script shows the last few completed games and next several
upcoming games for a specified team in a formatted ASCII table.

Usage:
    python team_schedule.py [team_name]

Examples:
    python team_schedule.py "San Francisco Giants"
    python team_schedule.py "New York Yankees"
    python team_schedule.py  # defaults to San Francisco Giants
"""

import argparse
from datetime import datetime, timedelta

from mlb import MlbClient, Game, Team


def get_opponent_str(game: Game, team_id: int) -> str:
    """Format the opponent string (with @ for away games)."""
    if game.home_team.id == team_id:
        return game.away_team.abbreviation
    else:
        return f"@ {game.home_team.abbreviation}"


def get_result_str(game: Game, team_id: int) -> str:
    """Format the result/time string."""
    if game.is_completed:
        if game.is_tie:
            return f"T {game.away_team_score}-{game.home_team_score}"
        elif game.winning_team and game.winning_team.id == team_id:
            return f"W {game.winning_team_score}-{game.losing_team_score}"
        else:
            return f"L {game.losing_team_score}-{game.winning_team_score}"
    elif game.is_in_progress:
        return f"{game.away_team_score}-{game.home_team_score} ({game.state})"
    else:
        # Future game - show time
        local_time = game.start_time.astimezone()
        return local_time.strftime("%I:%M %p").lstrip("0")


def get_record_str(game: Game, team_id: int) -> str:
    """Get the team's record at the time of the game."""
    if game.home_team.id == team_id:
        team = game.home_team
    else:
        team = game.away_team
    return f"{team.record_wins}-{team.record_losses}"


def get_day_str(date: datetime) -> str:
    """Format the day string, with 'TODAY' for current date."""
    if date.date() == datetime.now().date():
        return "TODAY"
    return date.strftime("%a")


def print_table(games: list[Game], team: Team, past_count: int) -> None:
    """Print games in a formatted ASCII table."""
    if not games:
        print("No games found.")
        return

    # Build table data
    rows = []
    for i, game in enumerate(games):
        is_past = i < past_count
        rows.append({
            "date": game.date.strftime("%m/%d"),
            "day": get_day_str(game.date),
            "opponent": get_opponent_str(game, team.id),
            "result": get_result_str(game, team.id),
            "record": get_record_str(game, team.id) if is_past or game.is_in_progress else "",
            "type": game.game_type,
            "is_past": is_past,
        })

    # Calculate column widths
    col_widths = {
        "date": max(5, max(len(r["date"]) for r in rows)),
        "day": max(5, max(len(r["day"]) for r in rows)),
        "opponent": max(8, max(len(r["opponent"]) for r in rows)),
        "result": max(6, max(len(r["result"]) for r in rows)),
        "record": max(6, max(len(r["record"]) for r in rows) if any(r["record"] for r in rows) else 6),
    }

    # Print header
    header = (
        f"{'Date':<{col_widths['date']}}  "
        f"{'Day':<{col_widths['day']}}  "
        f"{'Opponent':<{col_widths['opponent']}}  "
        f"{'Result':<{col_widths['result']}}  "
        f"{'Record':<{col_widths['record']}}"
    )
    separator = "-" * len(header)

    print(f"\n{team.name} Schedule")
    print(separator)
    print(header)
    print(separator)

    # Print rows
    divider_printed = False
    for row in rows:
        if not row["is_past"] and not divider_printed:
            print(separator)
            divider_printed = True

        # Mark preseason games
        type_marker = "*" if row["type"] == "PS" else " "

        line = (
            f"{row['date']:<{col_widths['date']}}  "
            f"{row['day']:<{col_widths['day']}}  "
            f"{row['opponent']:<{col_widths['opponent']}}  "
            f"{row['result']:<{col_widths['result']}}  "
            f"{row['record']:<{col_widths['record']}}"
            f"{type_marker}"
        )
        print(line)

    print(separator)
    print("* = preseason game")


def main():
    parser = argparse.ArgumentParser(
        description="Display recent and upcoming games for an MLB team."
    )
    parser.add_argument(
        "team",
        nargs="?",
        default="San Francisco Giants",
        help="Team name (default: San Francisco Giants)",
    )
    parser.add_argument(
        "--past",
        type=int,
        default=3,
        help="Number of past games to show (default: 3)",
    )
    parser.add_argument(
        "--future",
        type=int,
        default=7,
        help="Number of future games to show (default: 7)",
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
        print(f"Error: Team '{args.team}' not found.")
        print("\nAvailable teams:")
        for t in sorted(client.get_teams(), key=lambda x: x.name):
            print(f"  {t.name}")
        return 1

    # Get games for a reasonable date range
    today = datetime.now()
    start_date = today - timedelta(days=30)  # Look back for past games
    end_date = today + timedelta(days=60)    # Look ahead for future games

    all_games = team.get_games(
        start_date=start_date,
        end_date=end_date,
        include_preseason=args.preseason,
    )

    # If no games found, try extending the search (e.g., offseason)
    if not all_games:
        end_date = today + timedelta(days=120)
        all_games = team.get_games(
            start_date=start_date,
            end_date=end_date,
            include_preseason=True,  # Include preseason when searching wider
        )

    # Sort by date
    all_games.sort(key=lambda g: g.date)

    # Split into past and future
    past_games = [g for g in all_games if g.is_completed]
    future_games = [g for g in all_games if not g.is_completed]

    # Take the requested number from each
    past_games = past_games[-args.past:] if past_games else []
    future_games = future_games[:args.future] if future_games else []

    # Combine for display
    display_games = past_games + future_games

    print_table(display_games, team, len(past_games))
    return 0


if __name__ == "__main__":
    exit(main())
