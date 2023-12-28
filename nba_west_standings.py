import json
from lib.nba_api.stats.endpoints.leaguestandings import LeagueStandings

def get_western_conference_standings():
    standings_data = LeagueStandings().get_dict()
    eastern_conference_teams = [row for row in standings_data["resultSets"][0]["rowSet"] if row[5] == 'West']
    
    results = []
    for index, team in enumerate(eastern_conference_teams, start=1):
        team_name = team[4]
        wins = team[12]
        losses = team[13]
        games_behind = team[37]

        title = f"{team_name} {wins}-{losses} ({games_behind} GB)"
        subtitle = ""
        arg = ""
        icon = f"./nba_logos/{team_name}.svg"

        if index == 6:
            subtitle = "------ PLAYIN START ------"
        elif index == 10:
            subtitle = "------ PLAYIN END ------"
        
        result = {"title": title, "subtitle": subtitle, "arg": arg, "icon": {"path": icon}}
        results.append(result)

    return results

if __name__ == "__main__":
    standings_json = json.dumps({"items": get_western_conference_standings()})
    print(standings_json)