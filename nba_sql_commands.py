from datetime import datetime
import nba_data
import random

# Initializes database with empty tables
def initializeDBFromFile(cursor, filename):
    print("Initializing database...")
    fd = open(filename, 'r')
    sql_file = fd.read()
    fd.close()
    sql_commands = sql_file.split(';')
    try:
        for command in sql_commands:
            if command.strip() != '':
                cursor.execute(command)
        print("Successfully initialized database.")
    except Exception as e:
        print(f"Error in initializing: {e}")

# --- HELPER FUNCTIONS ---
# Reading from desired table
def read(cursor, table):
    print("Reading...")
    cursor.execute("SELECT * FROM {};".format(table))
    for row in cursor:
        print(f'row = {row}')
    print()

def existsInTable(cursor, table, atr, val):
    statement = f"SELECT * FROM {table} WHERE {atr} = {val};"
    cursor.execute(statement)
    return cursor.fetchall()

def updateTable(cursor, table, atr, val, condition):
    statement = f"UPDATE {table} " \
                f"SET {atr} = {val} " \
                f"WHERE {condition};"
    cursor.execute(statement)

def fetchFromDatabase(cursor, table, item="*", condition=""):
    try:
        if condition != "":
            cursor.execute(f"SELECT {item} FROM {table} WHERE {condition};")
        else:
            cursor.execute(f"SELECT {item} FROM {table};")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error in \'fetchFromDatabase\': {e}")
        return False

# --- POPULATING TABLES ---
# Populate "team" table
def insertTeamStats(cursor):
    statement = "INSERT INTO team(Name, City, Division, Conference, Wins, Losses) " \
                "VALUES(%s, %s, %s, %s, %s, %s);"
    try:
        for data in nba_data.getTeamStatsData():
            cursor.execute(statement, (data[0], data[1], data[2], data[3], data[4], data[5]))
        print("Team stats successfully inserted!")
    except Exception as e:
        print(f"Error in \'insertTeamStats\': {e}\n")

# Populate "players" table
def insertPlayerData(cursor):
    statement = "INSERT INTO players(Id, Name, Birthdate, Height, Position, Team) " \
                "VALUES(%s, %s, %s, %s, %s, %s);"
    try:
        for data in nba_data.getPlayerData():
            cursor.execute(statement, (data[0], data[1], data[2], data[3], data[4], data[5]))
        print("Player traits successfully inserted!")
    except Exception as e:
        print(f"Error in \'insertPlayerData\': {e}\n")

# Populate "playerstats" table
def insertPlayerStats(cursor):
    statement = "INSERT INTO playerstats(GP, PPG, RPG, APG, SPG, BPG, TOV, PlayerID) " \
                "VALUES(%s, %s, %s, %s, %s, %s, %s, %s);"
    try:
        for data in nba_data.getPlayerStatsData():
            id_num = data[7]
            if existsInTable(cursor,"players", "id", id_num):
                cursor.execute(statement, (data[0], data[1], data[2], data[3],data[4], data[5],
                                           data[6], data[7]))
        print("Player stats successfully inserted!")
    except Exception as e:
        print(f"Error in \'insertPlayerStats\': {e}\n")

# Populate "user" table
def insertUser(cursor, user_details_arr):
    statement = "INSERT INTO user(Id, Name, Email, Birthdate, Password, Joined, IsSignedIn) " \
                "VALUES(%s, %s, %s, %s, %s, %s, %s);"
    try:
        bday_dt = datetime.strptime(user_details_arr[2], "%m/%d/%y")
        user_arr = fetchFromDatabase(cursor, "user")
        cursor.execute(statement, (len(user_arr) + random.randint(355, 999999),   # ID
                                   user_details_arr[0],   # Name
                                   user_details_arr[1],   # Email
                                   bday_dt,               # Birthdate
                                   user_details_arr[3],   # Password
                                   datetime.now(),        # Time Joined
                                   False))                # IsSignedIn
        print("User successfully inserted!")
    except Exception as e:
        print(f"Error in \'insertUser\': {e}\n")

# Get "user" table
def userExists(cursor, user_details_arr):
    if len(user_details_arr) == 2:  # Contains email AND password (for signing in)
        statement = f"SELECT * FROM user WHERE email = %s AND password = %s;"
        cursor.execute(statement, (user_details_arr[0], user_details_arr[1]))
    else:  # Contains just email (for signing up)
        statement = f"SELECT * FROM user WHERE email = %s;"
        cursor.execute(statement, (user_details_arr[0],))
    try:
        return cursor.fetchall()
    except Exception as e:
        print(f"Error in signing in: {e}")

