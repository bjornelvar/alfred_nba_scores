import json
import urllib.request
import urllib.parse
import sys
from datetime import date

NBA_STANDINGS_URL = "https://stats.nba.com/stats/leaguestandings"
HEADERS = {
    "Host": "stats.nba.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
    "Accept-Language": "en-US,en;q=0.9",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
}

def get_current_season() -> str:
    """Return the NBA season string for today, e.g. '2024-25' if month<10 in 2025."""
    today = date.today()
    year = today.year
    if today.month >= 10:
        start, end = year, year + 1
    else:
        start, end = year - 1, year
    return f"{start}-{str(end)[2:]}"

def fetch_and_save_raw(league_id="00", season=None, season_type="Regular Season"):
    if season is None:
        season = get_current_season()
    qs = urllib.parse.urlencode({
        "LeagueID": league_id,
        "Season": season,
        "SeasonType": season_type,
    })
    url = f"{NBA_STANDINGS_URL}?{qs}"
    req = urllib.request.Request(url, headers=HEADERS, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        text = resp.read().decode("utf-8")

    return json.loads(text)

def get_conference_items(data, conference: str) -> list[dict]:
    conf = conference.strip().lower().capitalize()
    if conf not in ("East", "West"):
        raise ValueError("Conference must be 'East' or 'West'")

    rows = data["resultSets"][0]["rowSet"]
    filtered = [r for r in rows if r[5] == conf]  # index 5 is Conference

    items = []
    for idx, t in enumerate(filtered, start=1):
        name       = t[4]   # TeamName
        wins       = t[12]  # WINS
        losses     = t[13]  # LOSSES
        games_back = t[37]  # ConferenceGamesBack

        subtitle = ""

        items.append({
            "title":    f"{idx} {name} {wins}-{losses} ({games_back} GB)",
            "subtitle": subtitle,
            "arg":      "",
            "icon":     {"path": f"./nba_logos/{name.lower()}.svg"},
        })

    return items

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <east|west>")
        sys.exit(1)

    conference = sys.argv[1]
    try:
        data = fetch_and_save_raw()
        alfred_items = get_conference_items(data, conference)
        print(json.dumps({"items": alfred_items}))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
