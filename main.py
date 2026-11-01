from time import sleep
import requests
import sqlite3
BASE_URL = "https://api-web.nhle.com/v1"
PLAYER_ENDPOINT = "/player" 
LANDING = "/landing"
ROSTER_ENDPOINT = ["/roster", "/current"]
TEAM_ABBREVIATIONS = [
  "/ANA", "/BOS", "/BUF", "/CGY", "/CAR", "/CHI", "/COL", "/CBJ", 
  "/DAL", "/DET", "/EDM", "/FLA", "/LAK", "/MIN", "/MTL", "/NSH", 
  "/NJD", "/NYI", "/NYR", "/OTT", "/PHI", "/PIT", "/SJS", "/SEA", 
  "/STL", "/TBL", "/TOR", "/UTA", "/VAN", "/VGK", "/WSH", "/WPG"
]
ABBREVIATIONS_TO_NAMES = {
  "/ANA": "Anaheim Ducks", "/BOS": "Boston Bruins",
  "/BUF": "Buffalo Sabres", "/CGY": "Calgary Flames",
  "/CAR": "Carolina Hurricanes", "/CHI": "Chicago Blackhawks",
  "/COL": "Colorado Avalanche", "/CBJ": "Columbus Blue Jackets",
  "/DAL": "Dallas Stars", "/DET": "Detroit Red Wings",
  "/EDM": "Edmonton Oilers", "/FLA": "Florida Panthers",
  "/LAK": "Los Angeles Kings", "/MIN": "Minnesota Wild",
  "/MTL": "Montreal Canadiens", "/NSH": "Nashville Predators",
  "/NJD": "New Jersey Devils", "/NYI": "New York Islanders",
  "/NYR": "New York Rangers", "/OTT": "Ottawa Senators",
  "/PHI": "Philadelphia Flyers", "/PIT": "Pittsburgh Penguins",
  "/SJS": "San Jose Sharks", "/SEA": "Seattle Kraken",
  "/STL": "St Louis Blues", "/TBL": "Tampa Bay Lightning",
  "/TOR": "Toronto Maple Leafs", "/UTA": "Utah Hockey Club",
  "/VAN": "Vancouver Canucks", "/VGK": "Vegas Golden Knights",
  "/WSH": "Washington Capitals", "/WPG": "Winnipeg Jets"
}

def main():
    create_db()
    populate_db()
    

def get_player_stats(id: int):
    request = BASE_URL + PLAYER_ENDPOINT + "/" + str(id) + LANDING
    # print(request)
    response = requests.get(request)
    if response.status_code == 200:     
        data = response.json()
        name = f"{data['firstName']['default']} {data['lastName']['default']}"
        player = player_info(data)
        player_stats = data['featuredStats']['regularSeason']['subSeason']
        player[name] = [{**player[name][0], **player_stats}]
        return [name, player]
    else:
        print(response)
        print(request)

def get_rosters(team_abbreviations):
    request_beginning = BASE_URL+ROSTER_ENDPOINT[0]
    request_end =  ROSTER_ENDPOINT[1]
    teams = {}
    for team in team_abbreviations:
        team_name = ABBREVIATIONS_TO_NAMES[team]
        players = []
        request = request_beginning + team + request_end
        response = requests.get(request)
        if response.status_code == 200:
            data = response.json()
            forwards = data["forwards"]
            defensemen = data["defensemen"]
            goalies = data["goalies"]
            for player in forwards:
                try:
                    players.append(get_player_stats(player["id"]))
                except:
                    print("ERROR")
                    
            for player in defensemen:
                try:
                    players.append(get_player_stats(player["id"]))
                except:
                    print("ERROR")

            for player in goalies:
                try:
                    players.append(get_player_stats(player["id"]))
                except:
                    print("ERROR")

            teams[team_name] = players
        else:
            print(response)
            print(request)

        # print(teams)

    return teams

def player_info(player):
    name = f"{player['firstName']['default']} {player['lastName']['default']}"
    try:
        position = player["positionCode"]
    except:
        position = player["position"]
    
    try:
        id = player["id"]
    except:
        id = player["playerId"]
    return {name: [{"position": position, "id": id}]}

def create_db():
    connection = sqlite3.connect("NHL_Player_Stats.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT,
            team TEXT,
            games_played INTEGER,
            assists INTEGER,
            goals INTEGER,
            plus_minus INTEGER,
            points INTEGER,
            power_play_points INTEGER,
            shots INTEGER,
            shooting_percentage REAL,
            goals_against_avg REAL,
            losses INTEGER,
            ot_losses INTEGER,
            save_pct REAL,
            shutouts INTEGER,
            wins INTEGER
        )
    """)

    connection.commit()
    connection.close()

def update_db(rosters):
    connection = sqlite3.connect("NHL_Player_Stats.db")
    cursor = connection.cursor()
    for team, players in rosters.items():
        # print(players)
        for player in players:
            # print(player)
            player_name = player[0]
            player = player[1][player_name][0]
            cursor.execute("""
                INSERT OR REPLACE INTO players (
                    id, name, position, team, games_played, assists,
                    goals, plus_minus, points, power_play_points,
                    shots, shooting_percentage,
                    goals_against_avg, losses, ot_losses,
                    save_pct, shutouts, wins
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
            player["id"],
            player_name,
            player["position"],
            team,
            player.get("gamesPlayed"),
            player.get("assists"),
            player.get("goals"),
            player.get("plusMinus"),
            player.get("points"),
            player.get("powerPlayPoints"),
            player.get("shots"),
            player.get("shootingPctg"),
            player.get("goalsAgainstAvg"),
            player.get("losses"),
            player.get("otLosses"),
            player.get("savePctg"),
            player.get("shutouts"),
            player.get("wins")
        ))
    connection.commit()
    connection.close()

def query_db(query: str): 
    """
    Takes string as input
    example query and output:
    input:
    """ 
    # query_db("""SELECT name, games_played, goals, assists, points, plus_minus
    # FROM players
    # WHERE position != 'G' AND games_played < 20
    # ORDER BY points DESC
    # LIMIT 10""")
    """
    output (as of Oct. 31, 2026):
        ('Connor McDavid', 14, 8, 29, 37, 18)
        ('Leon Draisaitl', 14, 12, 14, 26, 13)
        ('Kirill Kaprizov', 15, 14, 10, 24, 10)
        ('Auston Matthews', 15, 10, 13, 23, 6)
        ('Evan Bouchard', 14, 7, 16, 23, 20)
        ('Nathan MacKinnon', 13, 8, 14, 22, 4)
        ('Tim Stützle', 15, 9, 12, 21, 6)
        ('Jack Eichel', 15, 7, 13, 20, 8)
        ('Matthew Tkachuk', 14, 4, 16, 20, 1)
        ('Quinn Hughes', 15, 4, 16, 20, 8)
    """
    connection = sqlite3.connect("NHL_Player_Stats.db")
    cursor = connection.cursor()

    cursor.execute(query)

    for player in cursor.fetchall():
        print(player)

    connection.close()

def populate_db():
    for i in range(31, 32):
        print(TEAM_ABBREVIATIONS[i])
        if i == 31:
            rosters = get_rosters(TEAM_ABBREVIATIONS[i:])
        else: 
            rosters = get_rosters(TEAM_ABBREVIATIONS[i:i+1])
            sleep(60) # sleeps due to too many call errors

        update_db(rosters)


if __name__ == main():
    main()