import mysql.connector
import nba_sql_commands
import nba_gui

# Connecting to database...
try:
    db = mysql.connector.connect(user="root", passwd="root", host="localhost", db="336_project")
    cursor = db.cursor()
except mysql.connector.errors.ProgrammingError as e:
    print(f"Looks like this is your first time running this: {e}.\n"
          f"Let's make a new database for you.")
    db = mysql.connector.connect(user="root", passwd="root", host="localhost")
    cursor = db.cursor()
    statement = "CREATE DATABASE IF NOT EXISTS 336_project;"
    cursor.execute(statement)
    nba_sql_commands.initializeDBFromFile(cursor, 'nba_database.sql')
    db.commit()

# --- REBUILD DATABASE ---
# OPTIONAL: If you want updated results, uncomment the lines between the boundaries and run.
# WARNING: This will take at least 15 minutes until complete.
# ===================================================================
# nba_sql_commands.insertTeamStats(cursor)
# nba_sql_commands.insertPlayerData(cursor)
# nba_sql_commands.insertPlayerStats(cursor)
# db.commit()
# ===================================================================

# --- GUI ---
nba_gui.generateGUI(cursor, db)
db.commit()

db.close()