import sqlite3
import requests
from datetime import datetime, timedelta,date
from models.nhl_score import nhl_score 


def create_system_tables(dbCursor, dbConnection):
    # create system tables tables
    query = '''
        CREATE TABLE IF NOT EXISTS nhl_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            home_team TEXT NOT NULL,
            home_team_image TEXT NOT NULL,
            away_team TEXT NOT NULL,
            away_team_image TEXT NOT NULL,
            home_score INTEGER NOT NULL,
            away_score INTEGER NOT NULL,
            first_period_home_score integer not null,
            second_period_home_score integer not null,
            third_period_home_score integer not null,
            overtime_home_score integer not null,
            final_home_score integer not null,
            first_period_away_score integer not null,
            second_period_away_score integer not null,
            third_period_away_score integer not null,
            overtime_away_score integer not null,
            final_away_score integer not null,
            round text not null,
            game_number integer not null,
            series_info text not null,
            DateCreated DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
    # Execute the SQL command
    dbCursor.execute(query)
    # Commit the changes
    dbConnection.commit()
    
    query = ""
    query = '''
        CREATE TABLE IF NOT EXISTS nhl_skating_leaders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank integer not null,
            player_name text not null,
            team_name text not null,
            points integer not null,
            datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
    # Execute the SQL command
    dbCursor.execute(query)
    # Commit the changes
    dbConnection.commit()

    query = '''    
        CREATE TABLE IF NOT EXISTS nhl_goal_tending_leaders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank integer not null,
            player_name text not null,
            team_name text not null,
            gaa float not null,
            datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
    # Execute the SQL command
    dbCursor.execute(query)
    # Commit the changes
    dbConnection.commit()

    query = '''
        CREATE TABLE IF NOT EXISTS nhl_goals_leaders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank integer not null,
            player_name text not null,
            team_name text not null,
            goals integer not null,
            datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
    # Execute the SQL command
    dbCursor.execute(query)
    # Commit the changes
    dbConnection.commit()

    query = '''
        CREATE TABLE IF NOT EXISTS nhl_plus_minus_leaders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank integer not null,
            player_name text not null,
            team_name text not null,
            plus_minus integer not null,
            datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
    # Execute the SQL command
    dbCursor.execute(query)
    # Commit the changes
    conn.commit()

    query = '''
        CREATE TABLE IF NOT EXISTS nhl_save_percentage_leaders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank integer not null,
            player_name text not null,
            team_name text not null,
            save_percentage float not null,
            datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
    # Execute the SQL command
    dbCursor.execute(query)
    # Commit the changes
    dbConnection.commit()

    query = '''
        CREATE TABLE IF NOT EXISTS nhl_goalie_wins_leaders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank integer not null,
            player_name text not null,
            team_name text not null,
            wins integer not null,
            datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
    # Execute the SQL command
    dbCursor.execute(query)
    # Commit the changes
    dbConnection.commit()

    query = '''
        CREATE TABLE IF NOT EXISTS nhl_schedule_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series text not null,
            away_team text not null,
            home_team text not null,
            game_date text not null,
            game_time text not null,
            datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
    # Execute the SQL command
    dbCursor.execute(query)
    # Commit the changes
    dbConnection.commit()
    
    #dbConnection.close()
def get_nhl_playoff_game_dates():
    #Target end date (inclusive)
    target_date = date(2026, 4, 18)
    # Current date
    current_date = date.today()- timedelta(days=1)

    # Ensure we are not asking for a future date
    if current_date < target_date:
        print("Today is before 2026-04-18")
        return []
    else:
        # Generate list of dates
        delta = current_date - target_date
        date_list = []
        for i in range(delta.days + 1):
            day = target_date + timedelta(days=i)
            date_list.append(day.strftime("%Y-%m-%d"))

    # Print results
    # for d in date_list:
    #     print(d)
    print(date_list)
    return date_list
def get_nhl_scores(GameDate:str):
    url = "https://api-web.nhle.com/v1/score/"+GameDate+""
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching NHL scores: {response.status_code}")
        return None
def compile_nhl_scores():
    gameDates= get_nhl_playoff_game_dates()
    nhlScores = []
    for gameDate in gameDates:
        print("Getting NHL scores for "+gameDate+"")
        results = get_nhl_scores(gameDate)
        numberOfGames = len(results['games'])
        print("Number of games: "+str(numberOfGames))

        for i in range(numberOfGames):
            game_score= nhl_score()
            game_score.game_date = results['games'][i]['gameDate']
            game_score.home_team = results['games'][i]['homeTeam']['name']['default']
            game_score.home_team_image = results['games'][i]['homeTeam']['logo']
            game_score.away_team = results['games'][i]['awayTeam']['name']['default']
            game_score.away_team_image = results['games'][i]['awayTeam']['logo']
            
            if('score' in results['games'][i]['homeTeam']):
                game_score.home_score = results['games'][i]['homeTeam']['score']
            else:
                game_score.home_score = 0
            
            if('score' in results['games'][i]['awayTeam']):
                game_score.away_score = results['games'][i]['awayTeam']['score']
            else:
                game_score.away_score = 0
            
            # Series info
            game_score.round = results['games'][i]['seriesStatus']['round']
            game_score.game_number = results['games'][i]['seriesStatus']['gameNumberOfSeries']
            neededToWinSeries = results['games'][i]['seriesStatus']['neededToWin']
            game_score.series_info = ""
            topSeedWins = results['games'][i]['seriesStatus']['topSeedWins']
            bottomSeedWins = results['games'][i]['seriesStatus']['bottomSeedWins']
            topSeedName = results['games'][i]['seriesStatus']['topSeedTeamAbbrev']
            bottomSeedName = results['games'][i]['seriesStatus']['bottomSeedTeamAbbrev']
            if(topSeedWins == 0 and bottomSeedWins == 0):
                game_score.series_info = "Series has not started"
            elif(topSeedWins > bottomSeedWins and topSeedWins < neededToWinSeries):
                game_score.series_info = ""+topSeedName+" leads series "+str(topSeedWins)+"-"+str(bottomSeedWins)+""
            elif(topSeedWins > bottomSeedWins and topSeedWins == neededToWinSeries):
                game_score.series_info = ""+topSeedName+" wins series "+str(topSeedWins)+"-"+str(bottomSeedWins)+""
            elif(bottomSeedWins > topSeedWins and bottomSeedWins == neededToWinSeries):
                game_score.series_info = ""+bottomSeedName+" wins series "+str(bottomSeedWins)+"-"+str(topSeedWins)+""
            elif(bottomSeedWins > topSeedWins and bottomSeedWins < neededToWinSeries):
                game_score.series_info = ""+bottomSeedName+" leads series "+str(bottomSeedWins)+"-"+str(topSeedWins)+""
            elif(topSeedWins == bottomSeedWins):
                    game_score.series_info = "Series is tied "+str(topSeedWins)+"-"+str(bottomSeedWins)+""
            
            # game_score.away_score = results['games'][i]['awayTeam']['score']
            goalsCount = len(results['games'][i]['goals'])
            game_score.first_period_home_score = 0
            game_score.first_period_away_score = 0
            game_score.second_period_home_score = 0
            game_score.second_period_away_score = 0
            game_score.third_period_home_score = 0
            game_score.third_period_away_score = 0
            game_score.overtime_home_score = 0
            game_score.overtime_away_score = 0
            for goal in range(goalsCount):
                goalItem = results['games'][i]['goals'][goal]
                period = goalItem['period']
                homeTeamAbbrv = results['games'][i]['homeTeam']['abbrev']
                awayTeamAbbrv = results['games'][i]['awayTeam']['abbrev']
                if (period== 1):
                    if(homeTeamAbbrv == goalItem['teamAbbrev']):
                       game_score.first_period_home_score += 1    
                    elif(awayTeamAbbrv == goalItem['teamAbbrev']):
                        game_score.first_period_away_score += 1
                elif (period== 2):
                    if(homeTeamAbbrv == goalItem['teamAbbrev']):
                        game_score.second_period_home_score += 1    
                    elif(awayTeamAbbrv == goalItem['teamAbbrev']):
                        game_score.second_period_away_score += 1
                    
                elif (period== 3):
                    if(homeTeamAbbrv == goalItem['teamAbbrev']):
                        game_score.third_period_home_score += 1    
                    elif(awayTeamAbbrv == goalItem['teamAbbrev']):
                        game_score.third_period_away_score += 1
                elif (period== 4):
                    if(homeTeamAbbrv == goalItem['teamAbbrev']):
                        game_score.overtime_home_score += 1    
                    elif(awayTeamAbbrv == goalItem['teamAbbrev']):
                        game_score.overtime_away_score += 1
            game_score.final_home_score = results['games'][i]['homeTeam']['score']
            game_score.final_away_score = results['games'][i]['awayTeam']['score']
            nhlScores.append(game_score)
    return nhlScores
def clear_nhl_scores_from_db(dbCursor, dbConnection):
    print("Clearing NHL Scores from database")
    sqlQuery = '''delete from nhl_scores'''
    dbCursor.execute(sqlQuery)
    print("Commiting delete of NHL Scores to database")
    dbConnection.commit()
def save_nhl_scores_to_db(dbCursor, dbConnection):
    clear_nhl_scores_from_db(dbCursor, dbConnection)
    nhlScores = compile_nhl_scores()
    print("Insert NHL Scores into database")
    for score in nhlScores:
        # insert data into database.
        sqlQuery = '''insert into nhl_scores(date,home_team,home_team_image,away_team,away_team_image,home_score,away_score,
                                    first_period_home_score,second_period_home_score,third_period_home_score,overtime_home_score,
                                    final_home_score,first_period_away_score,second_period_away_score,third_period_away_score,
                                    overtime_away_score,final_away_score,round,game_number,series_info)
                    values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        data = (score.game_date, score.home_team, score.home_team_image, score.away_team, score.away_team_image, score.home_score, score.away_score, 
                score.first_period_home_score, score.second_period_home_score, score.third_period_home_score, score.overtime_home_score, score.final_home_score, 
                score.first_period_away_score, score.second_period_away_score, score.third_period_away_score, score.overtime_away_score, score.final_away_score, 
                score.round, score.game_number, score.series_info)
        
        dbCursor.execute(sqlQuery, data)
        print("Commiting NHL Scores to database")
        dbConnection.commit()
        print("NHL Scores for "+score.game_date+" Complete")
def import_nhl_scores(dbCursor, dbConnection):
    print("Importing NHL Scores into database")
    save_nhl_scores_to_db(dbCursor, dbConnection)
    print("NHL Scores import complete")
    
        
# create a connection to a sqllite database
print("Create connection to hockeyplayoffdb/hockeyplayoff.db")
conn = sqlite3.connect('../hockeyplayoffdb/hockeyplayoff.db')

# create a cursor object to run sql commands against database.
cursor = conn.cursor()

create_system_tables(cursor, conn)
import_nhl_scores(cursor, conn)

# closet connection to database.
conn.close()