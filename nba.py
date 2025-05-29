#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_URL  = "https://nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com/NBA/liveData/scoreboard/todaysScoreboard_00.json"
BASE_URL = "https://www.nba.com/game/"

def fetch_games():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.getcode()
            if status != 200:
                raise RuntimeError(f"Failed to fetch scoreboard: HTTP {status}")
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP Error {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"URL Error: {e.reason}") from e

    return data["scoreboard"]["games"]

def fix_mojibake(s: str) -> str:
    # Fixing stupid mojibake in the response
    try:
        return s.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s

def format_games(games):
    items = []
    for game in games:
        away = game["awayTeam"]
        home = game["homeTeam"]
        leaders = game["gameLeaders"]

        utc_dt = datetime.strptime(game["gameTimeUTC"], "%Y-%m-%dT%H:%M:%SZ")\
                      .replace(tzinfo=timezone.utc)
        local_dt = utc_dt.astimezone()
        gametime = local_dt.strftime("%H:%M %Z")
        status_text = game["gameStatusText"].strip()
        away_code, home_code, gid = away["teamTricode"], home["teamTricode"], game["gameId"]

        if game["gameStatus"] == 1:
            # If playoff game, display series info
            # Playoff game will have something in this field instead of "", playin games will have "" as well as regular season games
            if game["seriesGameNumber"] != "":
                subtitle = f"{gametime} - {game['seriesGameNumber']} ({game['seriesText']})"
            else:
                # Putting regular season record as well as the gametime.
                subtitle = f"{gametime} - {away_code} {away['wins']}-{away['losses']} {home_code} {home['wins']}-{home['losses']}"
            title = f"{away_code} @ {home_code}"
            arg = f"{BASE_URL}{away_code}-vs-{home_code}-{gid}"
        else:
            title  = f"{away_code} {away['score']} - {home['score']} {home_code} ({status_text})"
            al, hl = leaders["awayLeaders"], leaders["homeLeaders"]

            # recover any mojibake in the player names
            al_name = fix_mojibake(al['name'])
            hl_name = fix_mojibake(hl['name'])
            subtitle = (
                f"{al_name}: {al['points']}pts/{al['rebounds']}reb/{al['assists']}ast - "
                f"{hl_name}: {hl['points']}pts/{hl['rebounds']}reb/{hl['assists']}ast"
            )
            arg = f"{BASE_URL}{away_code}-vs-{home_code}-{gid}/box-score"

        items.append({"title": title, "subtitle": subtitle, "arg": arg})

    return items or [{"title": "No games!"}]

def main():
    games  = fetch_games()
    output = {"items": format_games(games)}
    sys.stdout.write(json.dumps(output))

if __name__ == "__main__":
    main()
