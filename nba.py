import sys
import json
from lib.nba_api.live.nba.endpoints.scoreboard import ScoreBoard
import lib.pytz as pytz
from datetime import datetime
from lib.tzlocal import get_localzone

class NBAScoreboard:
    def __init__(self):
        self.todays_games = ScoreBoard().get_dict()["scoreboard"]["games"]
        self.base_url = "https://www.nba.com/game/"
        self.utc_tz = pytz.utc  # UTC timezone
        self.local_tz = get_localzone()  # Local timezone

    def status_nomenclature(self, status):
        if status == "Final":
            return "F"

    def create_lists(self):
        data = {
            "scores_list": [],
            "gametime_list": [],
            "gamestatus_list": [],
            "player_leaders": []
        }

        for game in self.todays_games:
            game_time_utc = datetime.strptime(game["gameTimeUTC"], '%Y-%m-%dT%H:%M:%SZ')
            game_time_local = game_time_utc.astimezone(self.local_tz)
            away_leader = game["gameLeaders"]["awayLeaders"]
            home_leader = game["gameLeaders"]["homeLeaders"]
            data["scores_list"].append([
                game["awayTeam"]["teamTricode"],
                game["awayTeam"]["score"],
                game["homeTeam"]["score"],
                game["homeTeam"]["teamTricode"],
            ])
            data["gametime_list"].append([
                game_time_local.strftime('%H:%M %Z'),
            ])
            data["gamestatus_list"].append([
                game["gameStatusText"],
            ])
            data["player_leaders"].append([
                away_leader["name"],
                away_leader["points"],
                away_leader["rebounds"],
                away_leader["assists"],
                home_leader["name"],
                home_leader["points"],
                home_leader["rebounds"],
                home_leader["assists"],
            ])

        return data
    
    def create_json_obj(self):
        '''
        Creating a JSON object to be used by Alfred
        '''
        data = self.create_lists()
        if len(data["scores_list"]) == 0:
            result = {"title": "No games!"}
            return [result]
        else:
            results = []
            for i, j in zip(data["scores_list"], data["player_leaders"]):
                game_index = data["scores_list"].index(i)
                game_status = self.todays_games[game_index]["gameStatus"]
                if game_status == 1:
                    # Game has not started
                    results.append({
                        "title": f"{i[0]} @ {i[3]}",
                        "subtitle": f"{data['gametime_list'][game_index][0]}",
                        "arg": f"{self.base_url}{self.todays_games[game_index]['awayTeam']['teamTricode']}-vs-{self.todays_games[game_index]['homeTeam']['teamTricode']}-{self.todays_games[game_index]['gameId']}",
                    })
                else:
                    # Game has started or finished
                    results.append({
                        "title": f"{i[0]} {i[1]} - {i[2]} {i[3]}\t\t({data['gamestatus_list'][game_index][0]})",
                        "subtitle": f"{j[0]}: {j[1]}pts/{j[2]}reb/{j[3]}ast - {j[4]}: {j[5]}pts/{j[6]}reb/{j[7]}ast",
                        "arg": f"{self.base_url}{self.todays_games[game_index]['awayTeam']['teamTricode']}-vs-{self.todays_games[game_index]['homeTeam']['teamTricode']}-{self.todays_games[game_index]['gameId']}/box-score",
                    })
            return results

if __name__ == "__main__":
    alfred_json = json.dumps({
        "items": NBAScoreboard().create_json_obj()
    })
    sys.stdout.write(alfred_json)