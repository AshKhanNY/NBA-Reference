import tkinter as tk
import tkinter.font as font
import tkinter.messagebox as messagebox

import numpy as np
import pandas as pd
import nba_sql_commands
import time as time
from tkinter import *
from pandastable import Table
from functools import partial

# --- HELPER FUNCTIONS ---
def getLabel(window, text):
    return Label(window, text=text)

def getName(cursor, id):
    players = nba_sql_commands.fetchFromDatabase(cursor, "players")
    for player in players:
        if id == player[0]:
            return player[1]

def getSignedInUser(cursor):
    user = []
    try:
        user = nba_sql_commands.fetchFromDatabase(cursor, "user", condition="isSignedIn = 1")[0]
    except Exception as e:
        print(f"No user signed in: {e}")
    return user

def labelPacker(window, text, font_choice, side=TOP):
    Label(window, text=text, font=font_choice).pack(side=side)

def gridPosition(entity, row, col, pos=W):
    entity.grid(row=row, column=col, sticky=pos)

def centerWindow(root, w, h):
    # get screen width and height
    ws = root.winfo_screenwidth()  # width of the screen
    hs = root.winfo_screenheight()  # height of the screen
    # calculate x and y coordinates for the Tk root window
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    # set the dimensions of the screen and where it is placed
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

def doNothing():
    print("Do nothing")

# --- PLAYERS SUBMENU ---
def generatePlayerStatsWindow(cursor, db, player_id, team_name):  # Creates New Window
    player_stats = nba_sql_commands.fetchFromDatabase(cursor, "playerstats", condition=f"playerid = {player_id}")[0]
    player_traits = nba_sql_commands.fetchFromDatabase(cursor, "players", condition=f"id = {player_id}")[0]
    # Get specific player properties
    name = player_traits[1]
    birthday = str(player_traits[2])[:10]  # cuts off HH:MM:SS portion
    height = player_traits[3]
    position = player_traits[4]
    gp = player_stats[0]
    ppg = player_stats[1]
    rpg = player_stats[2]
    apg = player_stats[3]
    spg = player_stats[4]
    bpg = player_stats[5]
    tov = player_stats[6]
    # Creates new window for player
    statsWindow = Toplevel()
    statsWindow.title(name)

    # Puts Team Logo in top Left Corner
    teamPhoto = PhotoImage(file="logos/" + team_name + ".png")
    statsWindow.iconphoto(False, teamPhoto)
    statsWindow.geometry("1050x100")
    statsWindow.resizable(False, False)
    statsTable = pd.DataFrame(
        {'Birthdate': [birthday], 'Height (in)': [height], 'Position': [position], 'Team': [team_name],
         'GP': [gp], 'PPG': [ppg], 'RPG': [rpg], 'APG': [apg], 'SPG': [spg],
         'BPG': [bpg], 'TOV': [tov]})
    frame = tk.Frame(statsWindow)
    frame.pack(fill='both', expand=True)
    pt = Table(frame, dataframe=statsTable)
    pt.show()

    signInUserId = nba_sql_commands.fetchFromDatabase(cursor, "user", condition="isSignedIn = 1")[0][0]
    # Favorite Team Button
    if nba_sql_commands.fetchFromDatabase(cursor, "favoriteTeams",
                                          condition=f"teamName = \'{team_name}\' AND userID = {signInUserId}"):
        favTeam_btnText = "Unfavorite This Team"
    else:
        favTeam_btnText = "Favorite This Team"

    def addFavoriteTeam():
        # Checks state of whether this user favorites this team
        state = fav_team['text']
        if state == "Favorite This Team":
            insert_statement = "INSERT INTO favoriteTeams(teamName, userID) " \
                               "VALUES(%s, %s);"
            cursor.execute(insert_statement, (team_name, signInUserId))
        else:
            delete_statement = f"DELETE FROM favoriteTeams WHERE teamName = \'{team_name}\' AND userID = {signInUserId}"
            cursor.execute(delete_statement)
        db.commit()
        fav_team['text'] = "Favorite This Team" \
            if fav_team['text'] == "Unfavorite This Team" else "Unfavorite This Team"

    fav_team = Button(pt, text=favTeam_btnText, command=addFavoriteTeam)
    fav_team.pack(anchor=SW, side=LEFT)
    # Favorite Player Button
    if nba_sql_commands.fetchFromDatabase(cursor, "favoritePlayers",
                                          condition=f"playerId = {player_id} AND userID = {signInUserId}"):
        favPlayer_btnText = "Unfavorite This Player"
    else:
        favPlayer_btnText = "Favorite This Player"

    def addFavoritePlayer():
        # Checks state of whether this user favorites this player
        state = fav_player['text']
        if state == "Favorite This Player":
            insert_statement = "INSERT INTO favoritePlayers(playerID, userID) " \
                               "VALUES(%s, %s);"
            cursor.execute(insert_statement, (player_id, signInUserId))
        else:
            delete_statement = f"DELETE FROM favoritePlayers WHERE playerID = {player_id} AND userID = {signInUserId}"
            cursor.execute(delete_statement)
        db.commit()
        fav_player['text'] = "Favorite This Player" \
            if fav_player['text'] == "Unfavorite This Player" else "Unfavorite This Player"

    fav_player = Button(pt, text=favPlayer_btnText, command=addFavoritePlayer)
    fav_player.pack(anchor=SE, side=RIGHT)
    statsWindow.mainloop()

# --- Home SUBMENU ---
def generateHomeWindow(cursor, favorite):  # Creates New Window
    user_table = nba_sql_commands.fetchFromDatabase(cursor, "user", condition=f"isSignedIn = 1")[0]
    user = user_table[0]

    # Creates new window for home page
    homeWindow = Toplevel()
    homeWindow.title(f"{user_table[1]}'s Favorites Page")
    homeWindow.geometry()
    myFont = font.Font(size=15)
    # Puts Team Logo in top Left Corner
    teamPhoto = PhotoImage(file="logos/nbalogo.png")
    homeWindow.iconphoto(False, teamPhoto)

    fav_players = np.array(
        nba_sql_commands.fetchFromDatabase(cursor, "favoriteplayers", item="playerid", condition=f"userid = {user}"))
    fav_p = fav_players.flatten()
    fav_teams = np.array(
        nba_sql_commands.fetchFromDatabase(cursor, "favoriteteams", item="teamname", condition=f"userid = {user}"))
    fav_t = fav_teams.flatten()

    if favorite == "players" and fav_p == []:
        labelPacker(homeWindow, "No favorite players available.", myFont)
        homeWindow.mainloop()
        return
    if favorite == "teams" and fav_t == []:
        labelPacker(homeWindow, "No favorite teams available.", myFont)
        homeWindow.mainloop()
        return

    player_stats = []
    gp = []
    ppg = []
    rpg = []
    apg = []
    spg = []
    bpg = []
    tov = []
    for i in fav_p:
        player_stats = np.array(
            nba_sql_commands.fetchFromDatabase(cursor, "playerstats", condition=f"playerid = {i}")[0])
        gp.append(player_stats[0])
        ppg.append(player_stats[1])
        rpg.append(player_stats[2])
        apg.append(player_stats[3])
        spg.append(player_stats[4])
        bpg.append(player_stats[5])
        tov.append(player_stats[6])

    player_traits = []
    name = []
    height = []
    position = []
    team = []
    for j in fav_p:
        player_traits = np.array(nba_sql_commands.fetchFromDatabase(cursor, "players", condition=f"id = {j}")[0])
        name.append(player_traits[1])
        height.append(player_traits[3])
        position.append(player_traits[4])
        team.append(player_traits[5])

    team_stats = []
    for k in fav_t:
        team_stats.append(nba_sql_commands.fetchFromDatabase(cursor, "team", condition=f"name =\'{k}\'")[0])
    if favorite == 'players':
        fav_table = pd.DataFrame(data=(name, height, position, team, gp, ppg, rpg, apg, spg, bpg, tov)).T
        fav_table.columns = ['Name', 'Height (in)', 'Position', 'Team', 'GP', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'TOV']
    if favorite == 'teams' and team_stats != []:
        fav_table = pd.DataFrame(team_stats)
        fav_table.columns = ['Name', 'City', 'Division', 'Conference', 'Wins', 'Losses']

    fav_table = fav_table.sort_values(by=['Name'], ascending=True)

    # Display Favorites Table
    frame = tk.Frame(homeWindow)
    frame.pack(fill='both', expand=True)
    pt = Table(frame, dataframe=fav_table)
    pt.show()

    homeWindow.mainloop()

# --- Standings SUBMENU ---
def generateStandingsWindow(cursor, conf):  # Creates New Window
    team_stats = nba_sql_commands.fetchFromDatabase(cursor, "team")

    # Create Standings Data Frame
    team_stats = pd.DataFrame(team_stats)
    team_stats.columns = ['Name', 'City', 'Division', 'Conference', 'Wins', 'Losses']

    if conf == 'East':
        confName = team_stats[team_stats['Conference'] == 'West'].index
        team_stats.drop(confName, inplace=True)
    if conf == 'West':
        confName = team_stats[team_stats['Conference'] == 'East'].index
        team_stats.drop(confName, inplace=True)

    team_stats = team_stats.sort_values(by=['Wins'], ascending=False)

    # Creates new window for standings
    standingsWindow = Toplevel()
    standingsWindow.title(f'{conf} Conference Standings')
    standingsWindow.geometry()

    # Display Standings Table
    frame = tk.Frame(standingsWindow)
    frame.pack(fill='both', expand=True)
    pt = Table(frame, dataframe=team_stats)
    pt.show()

    standingsWindow.mainloop()

# --- TEAMS CASCADE ---
def generateTeamCascade(cursor, db, menu):
    teamsTable = nba_sql_commands.fetchFromDatabase(cursor, "team")
    playerTable = nba_sql_commands.fetchFromDatabase(cursor, "players")
    teams_menu = Menu(menu)  # Builds a team sub-menu under the Main Menu
    menu.add_cascade(label="Teams", menu=teams_menu)

    for team in teamsTable:  # Creates Menus of Team Names inside Teams menu
        team_name_menu = Menu(teams_menu)  # Menu Named after the Team
        team_name = team[0]
        team_city = team[1]
        team_full_name = f"{team_city} {team_name}"  # City followed by name (ex. NY Knicks)
        teams_menu.add_cascade(label=team_full_name, menu=team_name_menu)
        for player in playerTable:   # Creates List of Players on Team inside of that teams menu
            player_team = player[5]  # Name of Team the Player is on
            if player_team == team_name:
                player_name = player[1]
                player_id = player[0]
                team_name_menu.add_command(
                    label=player_name,
                    command=partial(generatePlayerStatsWindow, cursor, db, player_id, team_name)
                )

# --- STANDINGS MENU ---
def generateStandingsMenu(cursor, db, menu):
    standingsMenu = Menu(menu)
    menu.add_cascade(label="League Standings", menu=standingsMenu)
    standingsMenu.add_command(label="League", command=partial(generateStandingsWindow, cursor, 'League'))
    standingsMenu.add_command(label="East", command=partial(generateStandingsWindow, cursor, 'East'))
    standingsMenu.add_command(label="West", command=partial(generateStandingsWindow, cursor, 'West'))
    # partial(generateStandingsWindow, cursor, db)

# --- LEAGUE LEADERS DROP DOWN ---
def generateLeagueLeadersMenu(cursor, menu):
    # Each index represents a menu:
    # 0. leaders, 1. gp, 2. ppg, 3. rpg, 4. apg, 5. spg, 6. bpg, 7. tov
    stats_menus = [Menu(menu) for i in range(8)]
    menu.add_cascade(label="League Leaders", menu=stats_menus[0])
    stats_menu_labels = ["GP", "PPG", "RPG", "APG", "SPG", "BPG", "TOV"]
    for i in range(1, len(stats_menu_labels)):
        stats_menus[0].add_cascade(label=stats_menu_labels[i], menu=stats_menus[i+1])

    player_stats = nba_sql_commands.fetchFromDatabase(cursor, "playerstats")
    leagueLeaders = []
    for player in player_stats:
        leagueLeaders.append(player)

    for i in range(7):
        leagueLeaders.sort(key=lambda x: x[i], reverse=True)
        for j in range(10):
            stats_menus[i+1].add_command(
                label=f"{getName(cursor, leagueLeaders[j][7])}: {leagueLeaders[j][i]} {stats_menu_labels[i]}",
                command=doNothing
            )


# --- EDIT ACCOUNT WINDOW ---
def generateEditAccWindow(cursor, db, user_details):
    ea_root = Tk()
    ea_root.title("Edit Details")
    detail_label = ["Name: ", "Email: ", "Password: "]
    new_detail_label = ["New Name: ", "New Email: ", "New Password: "]
    user_id = user_details[0]
    x = 0
    y = 1
    # Text Input
    name_input = StringVar(ea_root)
    email_input = StringVar(ea_root)
    pwd_input = StringVar(ea_root)

    def updateName():
        if name_input.get() == "":
            label = getLabel(ea_root, "Empty account name.")
        else:
            nba_sql_commands.updateTable(cursor, "user", "name", f"\'{name_input.get()}\'", f"id = {user_id}")
            db.commit()
            label = getLabel(ea_root, "Updated account name!")
        gridPosition(label, 6, 1)
        ea_root.update()
        time.sleep(1.5)
        label.destroy()

    def updateEmail():
        if email_input.get() == "":
            label = getLabel(ea_root, "Empty email.")
        else:
            nba_sql_commands.updateTable(cursor, "user", "email", f"\'{email_input.get()}\'", f"id = {user_id}")
            db.commit()
            label = getLabel(ea_root, "Updated email!")
        gridPosition(label, 6, 1)
        ea_root.update()
        time.sleep(1.5)
        label.destroy()

    def updatePassword():
        if pwd_input.get() == "":
            label = getLabel(ea_root, "Empty password.")
        else:
            nba_sql_commands.updateTable(cursor, "user", "password", f"\'{pwd_input.get()}\'", f"id = {user_id}")
            db.commit()
            label = getLabel(ea_root, "Updated password!")
        gridPosition(label, 6, 1)
        ea_root.update()
        time.sleep(1.5)
        label.destroy()

    # Buttons for Updating
    name_update_btn = Button(ea_root, text="Update Name", command=updateName)
    email_update_btn = Button(ea_root, text="Update Email", command=updateEmail)
    pwd_update_btn = Button(ea_root, text="Update Password", command=updatePassword)
    # Position all labels, inputs, and buttons
    for i in range(3):
        text = detail_label[i]
        new_text = new_detail_label[i]
        gridPosition(getLabel(ea_root, text), x, 0, E)
        gridPosition(getLabel(ea_root, new_text), y, 0, E)
        x += 2
        y += 2
    gridPosition(getLabel(ea_root, user_details[1]), 0, 1)
    gridPosition(getLabel(ea_root, user_details[2]), 2, 1)
    password = user_details[4]
    if len(password) < 4:
        password = "*" * len(password)
    else:
        secret = (len(password) - 2) * "*"
        password = secret + password[(len(password) - 2):]
    gridPosition(getLabel(ea_root, password), 4, 1)

    gridPosition(Entry(ea_root, textvariable=name_input), 1, 1)
    gridPosition(Entry(ea_root, textvariable=email_input), 3, 1)
    gridPosition(Entry(ea_root, textvariable=pwd_input), 5, 1)

    gridPosition(name_update_btn, 1, 2)
    gridPosition(email_update_btn, 3, 2)
    gridPosition(pwd_update_btn, 5, 2)

# --- DELETE ACCOUNT WINDOW ---
def generateDeleteWindow(cursor, db, user_id):
    answer = messagebox.askquestion("Delete Account", "Are You Sure You Want to Delete Account?")
    if answer == 'yes':
        statement = f"DELETE FROM favoritePlayers WHERE userID = {user_id};"
        cursor.execute(statement)
        statement = f"DELETE FROM favoriteTeams WHERE userID = {user_id};"
        cursor.execute(statement)
        statement = f"DELETE FROM user WHERE id = {user_id};"
        cursor.execute(statement)
        db.commit()
    else:
        return

# --- ACCOUNT DETAILS WINDOW ---
def generateAccountWindow(cursor, db):
    acc_root = Tk()
    acc_root.title("Account Details")
    centerWindow(acc_root, 225, 190)
    user_details = getSignedInUser(cursor)
    if user_details:
        detail_label = ["User ID: ", "Name: ", "Email: ", "DOB: ", "Password: ", "Time Joined: "]
        for i in range(len(detail_label)):
            text = detail_label[i]
            detail = user_details[i]
            gridPosition(getLabel(acc_root, text), i, 0, E)
            if i == 3:  # Checks for DOB
                detail = str(detail)[:-9]
            if i == 4:  # Accommodates for password
                if len(detail) < 4:
                    detail = "*" * len(detail)
                else:
                    secret = (len(detail) - 2) * "*"
                    detail = secret + detail[(len(detail) - 2):]
            gridPosition(getLabel(acc_root, detail), i, 1, W)
        user_id = user_details[0]
        edit = Button(acc_root, text="Edit Account", command=partial(generateEditAccWindow, cursor, db, user_details))
        delete_acc = Button(acc_root, text="Delete Account", command=partial(generateDeleteWindow, cursor, db, user_id))
        gridPosition(edit, len(user_details) + 1, 0)
        gridPosition(delete_acc, len(user_details) + 2, 0)
    else:
        gridPosition(getLabel(acc_root, "No user signed in."), 0, 0, E)
    acc_root.mainloop()

# --- Update New Signed In User ---
def updateSignedIn(cursor, user_id):
    statement = f"UPDATE user SET IsSignedIn = 0 WHERE id != {user_id}"
    cursor.execute(statement)
    statement = f"UPDATE user SET IsSignedIn = 1 WHERE id = {user_id}"
    cursor.execute(statement)
    print(f"User with ID: {user_id} is now signed in. Previous user is signed out.")

# --- SIGN UP WINDOW ---
def generateSignUpWindow(cursor, db, root):
    su_root = Tk()
    su_root.title("Create Account")
    centerWindow(su_root, 300, 220)
    # Display
    signUpLabel = getLabel(su_root, "Enter credentials")
    nameLabel = getLabel(su_root, "Username: ")
    emailLabel = getLabel(su_root, "Email: ")
    bdayLabel = getLabel(su_root, "Birthday: ")
    pwdLabel = getLabel(su_root, "Password: ")
    # Text Input
    name_input = StringVar(su_root)
    email_input = StringVar(su_root)
    bday_input = StringVar(su_root)
    pwd_input = StringVar(su_root)
    labelArray = [signUpLabel, nameLabel, emailLabel, bdayLabel, pwdLabel]
    inputArray = [name_input, email_input, bday_input, pwd_input]
    # Positioning
    gridPosition(labelArray[0], 0, 0)
    for i in range(1, len(labelArray)):
        gridPosition(labelArray[i], i, 0, E)
    for i in range(len(inputArray)):
        gridPosition(Entry(su_root, textvariable=inputArray[i]), i+1, 1)

    def signUp():
        # Name, Email, Birthdate, Password
        data_arr = [name_input.get(), email_input.get(), bday_input.get(), pwd_input.get()]
        emailPwd_arr = [email_input.get(), pwd_input.get()]
        if nba_sql_commands.userExists(cursor, [emailPwd_arr[0]]):
            label = getLabel(su_root, "Email already exists!")
            gridPosition(label, len(labelArray) + 1, 1)
            su_root.update()
            time.sleep(3)
            label.destroy()
        else:
            nba_sql_commands.insertUser(cursor, data_arr)
            db.commit()
            label = getLabel(su_root, "Sign Up Complete!")
            gridPosition(label, len(labelArray) + 1, 1)
            su_root.update()
            time.sleep(1.5)
            su_root.destroy()
            # Update signed in person
            user_arr = nba_sql_commands.userExists(cursor, emailPwd_arr)[0]
            print("Signing up for: " + str(user_arr))
            user_id = user_arr[0]
            updateSignedIn(cursor, user_id)
            db.commit()
            refresh(cursor, db, root)

    sign_up_btn = Button(su_root, text="Sign Up!", command=signUp)
    gridPosition(sign_up_btn, 6, 0)
    su_root.mainloop()

# --- SIGN IN WINDOW ---
def generateSignInWindow(cursor, db, root):
    si_root = Tk()
    si_root.title("Sign In")
    centerWindow(si_root, 300, 220)
    # Display
    signInLabel = getLabel(si_root, "Enter credentials")
    emailLabel = getLabel(si_root, "Email: ")
    pwdLabel = getLabel(si_root, "Password: ")
    # Text Input
    email_input = StringVar(si_root)
    pwd_input = StringVar(si_root)
    # Positioning
    gridPosition(signInLabel, 0, 0)
    gridPosition(emailLabel, 1, 0)
    gridPosition(pwdLabel, 2, 0)
    gridPosition(Entry(si_root, textvariable=email_input), 1, 1)
    gridPosition(Entry(si_root, textvariable=pwd_input), 2, 1)

    def signIn():
        # Email, Password
        emailPwd_arr = [email_input.get(), pwd_input.get()]
        if nba_sql_commands.userExists(cursor, emailPwd_arr):
            label = getLabel(si_root, "Successfully signed in!")
            gridPosition(label, 3, 1)
            si_root.update()
            time.sleep(3)
            si_root.destroy()
            # Update signed in person
            user_arr = nba_sql_commands.userExists(cursor, emailPwd_arr)[0]
            print("Signing in for: " + str(user_arr))
            user_id = user_arr[0]
            updateSignedIn(cursor, user_id)
            db.commit()
            refresh(cursor, db, root)
        else:
            label = getLabel(si_root, "Failed to signed in.")
            gridPosition(label, 3, 1)
            si_root.update()
            time.sleep(2)
            label.destroy()

    sign_up_btn = Button(si_root, text="Sign In!", command=signIn)
    gridPosition(sign_up_btn, 3, 0)
    si_root.mainloop()

# --- SIGN OUT FUNCTION ---
def signOutUser(cursor, db, root):
    statement = f"UPDATE user SET IsSignedIn = 0"
    cursor.execute(statement)
    db.commit()
    refresh(cursor, db, root)

# --- ACCOUNT CASCADE ---
def generateAccountCascade(cursor, db, root, menu):
    accountMenu = Menu(menu)
    menu.add_cascade(label="Account", menu=accountMenu)
    accountMenu.add_command(label="Sign In", command=partial(generateSignInWindow, cursor, db, root))
    accountMenu.add_command(label="Sign Out", command=partial(signOutUser, cursor, db, root))
    accountMenu.add_command(label="Account Details", command=partial(generateAccountWindow, cursor, db))
    accountMenu.add_command(label="Create Account", command=partial(generateSignUpWindow, cursor, db, root))

# --- Home Screen ---
def generateHomeMenu(cursor, db, menu):
    homeMenu = Menu(menu)
    menu.add_cascade(label="Home", menu=homeMenu)
    homeMenu.add_command(label="Favorite Players", command=partial(generateHomeWindow, cursor, 'players'))
    homeMenu.add_command(label="Favorite Teams", command=partial(generateHomeWindow, cursor, 'teams'))

# --- REFRESH MAIN SCREEN ---
def refresh(cursor, db, root):
    root.destroy()
    generateGUI(cursor, db)

# --- MAIN SCREEN ---
def generateGUI(cursor, db):
    root = Tk()
    root.title("NBA Reference")
    centerWindow(root, 800, 600)

    photo = PhotoImage(file="logos/nbalogo.png")
    root.iconphoto(False, photo)

    menu = Menu(root)
    root.config(menu=menu)
    try:
        signed_in_user = nba_sql_commands.fetchFromDatabase(cursor, "user", condition="isSignedIn = 1")[0]
        label = getLabel(root, f"Currently signed in as: {signed_in_user[1]}")
    except Exception as e:
        print(f"Looks like no one is signed in: {e}")
        label = getLabel(root, "No user currently signed in. Create account or sign in!\n"
                               "Keep in mind that you are unable to favorite teams/players\n"
                               "and cannot view \'Favorite Teams\' or \'Favorite Players\'.")
    label.place(relx=0.0, rely=0.0, anchor='nw')
    refresh_btn = Button(root, text="Refresh", command=partial(refresh, cursor, db, root))
    refresh_btn.pack(anchor="ne")
    generateAccountCascade(cursor, db, root, menu)
    generateHomeMenu(cursor, db, menu)
    generateTeamCascade(cursor, db, menu)
    generateStandingsMenu(cursor, db, menu)
    generateLeagueLeadersMenu(cursor, menu)

    root.mainloop()