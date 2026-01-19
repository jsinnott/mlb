MLB API Client Documentation
=============================

A Python library for accessing MLB game and team data from the MLB Stats API.

Features
--------

- Fetch teams, leagues, divisions, and games from the MLB Stats API
- Type-safe parsing using Pydantic models
- Convenient domain classes with navigation methods
- TTL-based caching to reduce API calls

Quick Start
-----------

.. code-block:: python

    from mlb import MlbClient
    from datetime import datetime

    # Create a client
    client = MlbClient()

    # Get a team
    giants = client.get_team_by_name("San Francisco Giants")
    print(f"{giants.name} play in the {giants.division_name}")

    # Get games for a date range
    games = giants.get_games(
        start_date=datetime(2025, 4, 1),
        end_date=datetime(2025, 4, 30)
    )

    for game in games:
        if game.is_completed:
            result = "W" if game.winning_team.id == giants.id else "L"
            print(f"{game.date.strftime('%m/%d')}: {game.short_name} ({result})")

Installation
------------

.. code-block:: bash

    # Install the package
    pip install -e .

    # Also install jsinnott-utils from local path
    pip install /path/to/python-utils

Contents
--------

.. toctree::
   :maxdepth: 2

   api
   models

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
