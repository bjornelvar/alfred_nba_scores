import sys
import json
from lib.nba_api.live.nba.endpoints.scoreboard import ScoreBoard
import lib.pytz as pytz
from datetime import datetime
from lib.tzlocal import get_localzone

games = ScoreBoard().get_dict()

print(json.dumps(games, indent=4))

# export games to json
with open('games.json', 'w') as f:
    json.dump(games, f, indent=4)