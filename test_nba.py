#!/usr/bin/env python3
import sys
import json
from datetime import datetime, timezone

BASE_URL = "https://www.nba.com/game/"

def fix_mojibake(s: str) -> str:
    # Fixing stupid mojibake in the response
    try:
        return s.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def fetch_games():
    # read from a local JSON file instead of hitting the API
    path = "/Users/bjossi/GitHub/alfred_nba_scores/data/games.json"
    path = "/Users/bjossi/GitHub/alfred_nba_scores/data/01_nostart.json"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"File not found: {path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in {path}: {e}")
    return data["scoreboard"]["games"]

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
                # Just put game time if not a playoff game
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
    sys.stdout.write(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
