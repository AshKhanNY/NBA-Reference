from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import teaminfocommon
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import teams
from nba_api.stats.static import players
from nba_api.stats.library import parameters
import time as time

# Setting constants
LEAGUE_ID = parameters.LeagueID.nba
PER_MODE = parameters.PerMode36.totals
# Getting teams and players
team_dict = teams.get_teams()
player_dict = players.get_players()

# Takes in dataframe and attribute, and returns desired value
def getAttribute(df, attr):
    targets = [attr]
    y = df.loc[:, targets].values
    y = y.ravel()
    return y

# Extracting all team IDs
def allTeamIDs(team_dict):
    id_array = []
    for team in team_dict:
        if team['id'] not in id_array:  # prevents duplicate entries
            id_array.append(team['id'])
    return id_array
team_ids = allTeamIDs(team_dict)

# Extracting at most 100 player IDs for players that are active
def getPlayerIDs(player_dict):
    id_array = []
    for player in player_dict:
        if player['is_active']:
            p_id = player['id']
            id_array.append(p_id)
    return id_array
player_ids = getPlayerIDs(player_dict)

def getTeamStatsData():
    data_arr = []
    for id_num in team_ids:
        print("Working on team of ID: {}".format(id_num))
        stats = teaminfocommon.TeamInfoCommon(league_id=LEAGUE_ID, team_id=id_num)
        df = stats.get_data_frames()[0]
        time.sleep(.66)  # allows multiple calls to API
        name = getAttribute(df, "TEAM_NAME")[0]
        city = getAttribute(df, "TEAM_CITY")[0]
        division = getAttribute(df, "TEAM_DIVISION")[0]
        conference = getAttribute(df, "TEAM_CONFERENCE")[0]
        w = str(getAttribute(df, "W")[0])
        l = str(getAttribute(df, "L")[0])
        attributes = [name, city, division, conference, w, l]
        print(attributes)
        data_arr.append(attributes)
    print("Done processing team stats.")
    return data_arr

def getPlayerData():
    data_arr = []
    for id_num in player_ids:
        print("Working on traits of player of ID: {}".format(id_num))
        stats = commonplayerinfo.CommonPlayerInfo(player_id=id_num)
        df = stats.get_data_frames()[0]
        time.sleep(.66)  # allows multiple calls to API
        name = getAttribute(df, "FIRST_NAME")[0] + " " + getAttribute(df, "LAST_NAME")[0]
        birthdate = getAttribute(df, "BIRTHDATE")[0]
        height = getAttribute(df, "HEIGHT")[0].split("-")  # splits to feet and inches
        height_in_inches = int(height[0]) * 12 + int(height[1])
        position = getAttribute(df, "POSITION")[0]
        team = getAttribute(df, "TEAM_NAME")[0]
        if team != "":  # player must be labeled as part of a team
            attributes = [id_num, name, birthdate, height_in_inches, position, team]
            print(attributes)
            data_arr.append(attributes)
    print("Done processing player traits.")
    return data_arr

def getPlayerStatsData():  # Grabs stats of each player
    data_arr = []
    for id_num in player_ids:
        print("Working on stats of player of ID: {}".format(id_num))
        stats = playercareerstats.PlayerCareerStats(per_mode36=PER_MODE, player_id=id_num)
        df = stats.get_data_frames()[0]
        time.sleep(.75)  # allows multiple calls to API
        games_played = sum(getAttribute(df, "GP"))
        if games_played >= 1:  # checks if player has games played in record
            points_per_game = sum(getAttribute(df, "PTS")) / games_played
            rebounds_per_game = sum(getAttribute(df, "REB")) / games_played
            assists_per_game = sum(getAttribute(df, "AST")) / games_played
            steals_per_game = sum(getAttribute(df, "STL")) / games_played
            blocks_per_game = sum(getAttribute(df, "BLK")) / games_played
            tov_per_game = sum(getAttribute(df, "TOV")) / games_played
            attributes = [float(games_played), float(points_per_game),float(rebounds_per_game), float(assists_per_game),
                          float(steals_per_game), float(blocks_per_game), float(tov_per_game),id_num]
        else:
            attributes = [0, 0, 0, 0, 0, 0, 0, id_num]
        print(attributes)
        data_arr.append(attributes)
    print("Done processing player stats.")
    return data_arr