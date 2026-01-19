Pydantic API Models
===================

These models represent the raw JSON structures returned by the MLB Stats API.
They are used internally for parsing API responses and are typically not used
directly by library consumers.

For the user-facing domain models (Team, Game, League, Division), see the
:doc:`api` page.

Response Models
---------------

.. autoclass:: mlb.models.api.ScheduleResponse
   :members:
   :undoc-members:

.. autoclass:: mlb.models.api.TeamsResponse
   :members:
   :undoc-members:

.. autoclass:: mlb.models.api.LeaguesResponse
   :members:
   :undoc-members:

.. autoclass:: mlb.models.api.DivisionsResponse
   :members:
   :undoc-members:

Game Models
-----------

.. autoclass:: mlb.models.api.ApiGame
   :members:
   :undoc-members:

.. autoclass:: mlb.models.api.ApiGameStatus
   :members:
   :undoc-members:

.. autoclass:: mlb.models.api.ApiGameTeams
   :members:
   :undoc-members:

.. autoclass:: mlb.models.api.ApiGameTeam
   :members:
   :undoc-members:

Team Models
-----------

.. autoclass:: mlb.models.api.ApiTeam
   :members:
   :undoc-members:

League Models
-------------

.. autoclass:: mlb.models.api.ApiLeague
   :members:
   :undoc-members:

.. autoclass:: mlb.models.api.ApiSeasonDateInfo
   :members:
   :undoc-members:

Division Models
---------------

.. autoclass:: mlb.models.api.ApiDivision
   :members:
   :undoc-members:

Reference Models
----------------

These are small models used within other API responses.

.. autoclass:: mlb.models.api.ApiVenue
   :members:
   :undoc-members:

.. autoclass:: mlb.models.api.ApiLeagueRef
   :members:
   :undoc-members:

.. autoclass:: mlb.models.api.ApiDivisionRef
   :members:
   :undoc-members:

.. autoclass:: mlb.models.api.ApiTeamRef
   :members:
   :undoc-members:

.. autoclass:: mlb.models.api.ApiLeagueRecord
   :members:
   :undoc-members:
