import sqlite3
import requests
from datetime import datetime, timedelta,date

from sqlmodel import true
from src.data.hockeyplayoffetl.models.nhl_goaltending_win_leader import nhl_goaltending_win_leader
from src.data.hockeyplayoffetl.models.nhl_score import nhl_score
from .models.nhl_team import nhl_score
from .models.nhl_skate_leaders import nhl_skate_leader
from .models.data_request import data_request
from .models.nhl_goaltending_gaa_leader import nhl_goaltending_gaa_leader
from .models.nhl_goaltending_save_pct_leader import nhl_goaltending_save_pct_leader
from .models.nhl_skate_goal_leader import nhl_skate_goal_leader
import argparse
from .services.nhl_etl_manager import nhl_etl_manager
from .services.nhl_api_client import nhl_api_client
from .services.nhl_db_manager import nhl_db_manager
import os
from pathlib import Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
class NHLDataManager:
      dbConn = None
      dbCursor = None
      _dbFilePath = None
      _debugEnabled = False
      def __init__(self, DBFilePath:str, _debugEnabled:bool=False):
            self._dbFilePath = DBFilePath
            self._debugEnabled = _debugEnabled
            self.debugPrint("Create connection to hockeyplayoffdb/hockeyplayoff.db")
            self.dbConn = sqlite3.connect(self._dbFilePath)
            self.debugPrint("Create cursor object to run sql commands against database")
            # create a cursor object to run sql commands against database.
            self.debugPrint("Creating database cursor object.")
            self.dbCursor = self.dbConn.cursor()
            self.debugPrint("Database cursor object created.")

      def run_nhl_etl_process(self,ProvisionTables:bool)->bool:
          try:
              db_connection = sqlite3.connect(self._dbFilePath)
              # Initialize your managers
              api_client = nhl_api_client()
              db_manager = nhl_db_manager(self.dbConn)
              etl_manager = nhl_etl_manager(api_client, db_manager,True)

              if(ProvisionTables):
                 etl_manager.provision_app_tables()

              etl_manager.run_data_extraction_process()
              return True
          except sqlite3.Error as e:
                 print(f"Error connecting to database: {e}")
                 # Handle the error appropriately, maybe exit or log
                 exit()
          except Exception as e:
              self.debugPrint(f"Error occurred during data extraction process: {e}")
              return None

      def debugPrint(self, message:str):
         if(self._debugEnabled):
            print(message)
      def closeDBConnection(self):
            self.debugPrint("Closing database connection.")
            self.dbConn.close()
            self.debugPrint("Database connection closed.")
      def run_data_extraction_process(self):
          try:
              self.debugPrint("Starting data extraction process.")
              nhlScores = self.provision_app_tables(self.dbCursor, self.dbConn)
              self.debugPrint("Provisioning of database tables complete.")
              self.debugPrint("Importing NHL Scores into database.")
              self.import_nhl_scores(self.dbCursor, self.dbConn)
              self.debugPrint("Importing NHL Scores into database complete.")
              self.debugPrint("Saving NHL Teams to database.")
              self.save_nhl_teams_to_db(self.dbCursor, self.dbConn)
              self.debugPrint("Saving NHL Teams to database complete.")

              self.debugPrint("Getting NHL Skater Leaders and saving to database.")
              self.process_nhl_skater_leaders()
              self.debugPrint("Getting NHL Skater Leaders and saving to database complete.")

              self.debugPrint("Getting NHL Goaltending GAA Leaders and saving to database.")
              self.process_nhl_goaltending_gaa_leaders()
              self.debugPrint("Getting NHL Goaltending GAA Leaders and saving to database complete.")

              self.debugPrint("Getting NHL Goaltending Wins Leaders and saving to database.")
              self.process_nhl_goaltending_wins_leaders()
              self.debugPrint("Getting NHL Goaltending Wins Leaders and saving to database complete.")

              self.debugPrint("Getting NHL Goaltending Save Percentage Leaders and saving to database.")
              self.process_nhl_goaltending_savepct_leaders()
              self.debugPrint("Getting NHL Goaltending Save Percentage Leaders and saving to database complete.")

              self.debugPrint("Getting NHL Skate Goal Leaders and saving to database.")
              self.process_nhl_skate_goal_leaders()
              self.debugPrint("Getting NHL Skate Goal Leaders and saving to database complete.")

              self.closeDBConnection()
              self.debugPrint("Data extraction process complete.")
              return nhlScores
          except Exception as e:
              self.debugPrint(f"Error occurred during data extraction process: {e}")
              return None
      def provision_app_tables(self, DBCursor, DBConnection):
            self.debugPrint("Provisioning database tables")
            self.create_nhl_scores_table(DBCursor, DBConnection)
            #self.create_nhl_skating_leaders(DBCursor, DBConnection)
            #self.create_nhl_goal_tending_leaders(DBCursor, DBConnection)
            self.create_nhl_goals_leaders(DBCursor, DBConnection)
            self.create_nhl_plus_minus_leaders(DBCursor, DBConnection)
            self.create_nhl_save_percentage_leaders(DBCursor, DBConnection)
            self.create_nhl_goalie_wins_leaders(DBCursor, DBConnection)
            self.create_nhl_schedule_games(DBCursor, DBConnection)
            self.create_nhl_teams_table(DBCursor, DBConnection)
      def create_nhl_teams_table(self, DBCursor, DBConnection):
            try:
              query = '''
                    CREATE TABLE IF NOT EXISTS nhl_teams (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        team_name TEXT NOT NULL,
                        active BOOLEAN NOT NULL,
                        datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                    '''
                 # Execute the SQL command
              DBCursor.execute(query)
              # Commit the changes
              DBConnection.commit()
              return True
            except sqlite3.OperationalError as e:
              self.debugPrint(f"Error Message: {e}")
              self.debugPrint("Error occurred while creating nhl_teams table.")
              DBConnection.rollback()
              self.debugPrint("Rolled back the transaction.")
              DBConnection.close()
              self.debugPrint("Closed the database connection.")
              return False
      def create_nhl_goals_leaders(self, DBCursor, DBConnection):
            try:
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
              DBCursor.execute(query)
              # Commit the changes
              DBConnection.commit()
              return True
            except sqlite3.OperationalError:
              self.debugPrint("Error occurred while creating nhl_goals_leaders table.")
              DBConnection.rollback()
              self.debugPrint("Rolled back the transaction.")
              DBConnection.close()
              self.debugPrint("Closed the database connection.")
              return False
      def create_nhl_plus_minus_leaders(self, DBCursor, DBConnection):
            try:
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
              DBCursor.execute(query)
              # Commit the changes
              DBConnection.commit()
              return True
            except sqlite3.OperationalError:
              self.debugPrint("Error occurred while creating nhl_plus_minus_leaders table.")
              DBConnection.rollback()
              self.debugPrint("Rolled back the transaction.")
              DBConnection.close()
              self.debugPrint("Closed the database connection.")
              return False
      def create_nhl_save_percentage_leaders(self, DBCursor, DBConnection):
            try:
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
              DBCursor.execute(query)
              # Commit the changes
              DBConnection.commit()
              return True
            except sqlite3.OperationalError:
              self.debugPrint("Error occurred while creating nhl_save_percentage_leaders table.")
              DBConnection.rollback()
              self.debugPrint("Rolled back the transaction.")
              DBConnection.close()
              self.debugPrint("Closed the database connection.")
              return False
      def create_nhl_goalie_wins_leaders(self, DBCursor, DBConnection):
            try:
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
              DBCursor.execute(query)
              # Commit the changes
              DBConnection.commit()
              return True
            except sqlite3.OperationalError:
              self.debugPrint("Error occurred while creating nhl_goalie_wins_leaders table.")
              DBConnection.rollback()
              self.debugPrint("Rolled back the transaction.")
              DBConnection.close()
              self.debugPrint("Closed the database connection.")
              return False
      def create_nhl_schedule_games(self, DBCursor, DBConnection):
            try:
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
              DBCursor.execute(query)
              # Commit the changes
              DBConnection.commit()
              return True
            except sqlite3.OperationalError:
              self.debugPrint("Error occurred while creating nhl_schedule_games table.")
              DBConnection.rollback()
              self.debugPrint("Rolled back the transaction.")
              DBConnection.close()
              self.debugPrint("Closed the database connection.")
              return False
      def get_nhl_playoff_game_dates(self):
            #Target end date (inclusive)
            target_date = date(2026, 4, 18)
            # Current date
            current_date = date.today()- timedelta(days=1)

            # Ensure we are not asking for a future date
            if current_date < target_date:
                self.debugPrint("Today is before 2026-04-18")
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
            self.debugPrint(date_list)
            return date_list

      #---------------------------------------------------
      # Start - Get NHL Scores
      def create_nhl_scores_table(self, DBCursor, DBConnection):
            try:
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
              DBCursor.execute(query)
              # Commit the changes
              DBConnection.commit()
              return True
            except sqlite3.OperationalError:
              self.debugPrint("Error occurred while creating nhl_scores table.")
              DBConnection.rollback()
              self.debugPrint("Rolled back the transaction.")
              DBConnection.close()
              self.debugPrint("Closed the database connection.")
              return False
      def get_nhl_scores(self,GameDate:str):
            try:
                url = "https://api-web.nhle.com/v1/score/"+GameDate+""
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data
                else:
                    self.debugPrint(f"Error fetching NHL scores: {response.status_code}")
                    return None
            except Exception as e:
                   self.debugPrint(f"Exception occurred while fetching NHL scores: {e}")
                   return None
      def compile_nhl_scores(self):
          gameDates= self.get_nhl_playoff_game_dates()
          nhlScores = []
          for gameDate in gameDates:
              self.debugPrint("Getting NHL scores for "+gameDate+"")
              results = self.get_nhl_scores(gameDate)
              numberOfGames = len(results['games'])
              self.debugPrint("Number of games: "+str(numberOfGames))

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
      def clear_nhl_scores_from_db(self,dbCursor, dbConnection):
          try:
              self.debugPrint("Clearing NHL Scores from database")
              sqlQuery = '''delete from nhl_scores'''
              dbCursor.execute(sqlQuery)
              self.debugPrint("Commiting delete of NHL Scores to database")
              dbConnection.commit()
          except Exception as e:
              self.debugPrint("Error clearing NHL Scores from database: " + str(e))
      def save_nhl_scores_to_db(self,dbCursor, dbConnection):
          try:
              self.clear_nhl_scores_from_db(dbCursor, dbConnection)
              nhlScores = self.compile_nhl_scores()
              self.debugPrint("Insert NHL Scores into database")
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
                  self.debugPrint("Commiting NHL Scores to database")
                  dbConnection.commit()
                  self.debugPrint("NHL Scores for "+score.game_date+" Complete")
              return True
          except Exception as e:
                 self.debugPrint("Error saving NHL Scores to database: " + str(e))
                 dbConnection.rollback()
                 self.debugPrint("Rolled back the transaction.")
                 dbConnection.close()
                 self.debugPrint("Closed the database connection.")
                 return False
      # End - Get NHL Scores
      #---------------------------------------------------

      #---------------------------------------------------
      # Start - Get NHL Skater Leaders
      def process_nhl_skater_leaders(self):
            try:
                # create data table.
                processRequest = data_request()
                processRequest.dbCursor = self.dbCursor
                processRequest.dbConn = self.dbConn

                # create data table for nhl skating leaders.
                self.create_nhl_skating_leaders(processRequest)

                # get json data from api.
                processRequest.jsonData = self.get_nhl_skater_leaders()

                # clear existing data from database table.
                self.clear_nhl_skater_leaders_table_from_db(processRequest)

                # compile data into list of nhl_skate_leader objects.
                processRequest.entityData = self.compile_nhl_skater_leaders(processRequest)

                # save data to database.
                self.save_nhl_skater_leaders_to_db(processRequest)
                return True
            except Exception as e:
                self.debugPrint("process_nhl_skater_leaders - Error processing NHL skate leaders: " + str(e))
                return False
      def create_nhl_skating_leaders(self, request:data_request=None):
            try:
              query = '''
                    CREATE TABLE IF NOT EXISTS nhl_skating_leaders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rank integer not null,
                        first_name text not null,
                        last_name text not null,
                        headshot_url text not null,
                        team_name text not null,
                        teamlogo_url text not null,
                        points integer not null,
                        datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                    '''
                 # Execute the SQL command
              request.dbCursor.execute(query)
              # Commit the changes
              request.dbConn.commit()
              return True
            except sqlite3.OperationalError:
              self.debugPrint("Error occurred while creating nhl_skating_leaders table.")
              request.dbConn.rollback()
              self.debugPrint("Rolled back the transaction.")
              request.dbConn.close()
              self.debugPrint("Closed the database connection.")
              return False
      def get_nhl_skater_leaders(self):
          try:
              url = "https://api-web.nhle.com/v1/skater-stats-leaders/20252026/3?categories=goals&limit=5"
              response = requests.get(url)
              if response.status_code == 200:
                  data = response.json()
                  return data
              else:
                  self.debugPrint(f"Error fetching NHL skater leaders: {response.status_code}")
                  return None
          except Exception as e:
              self.debugPrint(f"Exception occurred while fetching NHL skater leaders: {e}")
              return None
      def compile_nhl_skater_leaders(self, request:data_request=None):
          try:
              nhlSkateLeadersList = request.jsonData
              nhlSkateLeaders = []
              counter = 0
              numberOfLeaders = len(nhlSkateLeadersList['goals'])
              self.debugPrint("Number of skater leaders: "+str(numberOfLeaders))
              for i in range(numberOfLeaders):
                  leader = nhlSkateLeadersList['goals'][i]
                  nhlSkateLeader = nhl_skate_leader()
                  nhlSkateLeader.rank = i+1
                  nhlSkateLeader.first_name = leader['firstName']['default']
                  nhlSkateLeader.last_name = leader['lastName']['default']
                  nhlSkateLeader.team_name = leader['teamName']['default']
                  nhlSkateLeader.points = leader['value']
                  nhlSkateLeader.headshot_url = leader['headshot']
                  nhlSkateLeader.teamlogo_url = leader['teamLogo']
                  nhlSkateLeaders.append(nhlSkateLeader)
              return nhlSkateLeaders
          except Exception as e:
              self.debugPrint("compile_nhl_skater_leaders - Error compiling NHL skate leaders: " + str(e))
              return []
      def clear_nhl_skater_leaders_table_from_db(self,request:data_request=None):
          try:
              self.debugPrint("Clearing NHL Skater Leaders from database")
              sqlQuery = '''delete from nhl_skating_leaders'''
              request.dbCursor.execute(sqlQuery)
              request.dbConn.commit()
              self.debugPrint("NHL Skater Leaders cleared from database successfully")
          except Exception as e:
              self.debugPrint("Error clearing NHL Skater Leaders from database: " + str(e))
              self.debugPrint("Error saving NHL Skater Leaders to database: " + str(e))
              request.dbConn.rollback()
              self.debugPrint("Rolled back the transaction.")
              request.dbConn.close()
              self.debugPrint("Closed the database connection.")
              exit(1)
      def save_nhl_skater_leaders_to_db(self, request:data_request=None):
            try:

                nhlSkateLeaders = request.entityData # self.compile_nhl_skater_leaders()
                self.debugPrint("Insert NHL Skater Leaders into database")
                for leader in nhlSkateLeaders:
                    # insert data into database.
                    sqlQuery = '''insert into nhl_skating_leaders(rank,first_name,last_name,team_name,points,headshot_url,teamlogo_url)
                                values(?,?,?,?,?,?,?)'''
                    data = (leader.rank, leader.first_name, leader.last_name, leader.team_name, leader.points, leader.headshot_url, leader.teamlogo_url)
                    request.dbCursor.execute(sqlQuery, data)
                    self.debugPrint("Commiting NHL Skater Leaders to database")
                    request.dbConn.commit()
                return True
            except Exception as e:
                     self.debugPrint("save_nhl_skater_leaders_to_db - Error saving NHL Skater Leaders to database: " + str(e))
                     request.dbConn.rollback()
                     self.debugPrint("Rolled back the transaction.")
                     request.dbConn.close()
                     self.debugPrint("Closed the database connection.")
                     exit(1)
      # End - Get NHL Skater Leaders
      #---------------------------------------------------
      #---------------------------------------------------
      # Start - Get NHL Goaltending GAA Leaders
      def create_nhl_goaltending_gaa_leaders_table(self, request:data_request=None)->bool:
          try:
              self.debugPrint("Creating "+ request.label +" table in database")
              query = '''
                    CREATE TABLE IF NOT EXISTS nhl_goaltending_gaa_leaders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rank integer not null,
                        first_name text not null,
                        last_name text not null,
                        team_name text not null,
                        gaa float not null,
                        headshot_url text not null,
                        teamlogo_url text not null,
                        datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                    '''
                 # Execute the SQL command
              request.dbCursor.execute(query)
              # Commit the changes
              request.dbConn.commit()
              self.debugPrint(request.label +" table created in database successfully")
              return True
          except sqlite3.OperationalError:
                 self.debugPrint("Error occurred while creating "+ request.label +" table.")
                 request.dbConn.rollback()
                 self.debugPrint("Rolled back the transaction.")
                 request.dbConn.close()
                 self.debugPrint("Closed the database connection.")
                 return False
      def get_nhl_goaltending_gaa_leaders_data(self) ->any:
          try:
              self.debugPrint("Fetching data from API")
              url = "https://api-web.nhle.com/v1/goalie-stats-leaders/20252026/3?categories=goalsAgainstAverage&limit=5"
              response = requests.get(url)
              if response.status_code == 200:
                  data = response.json()
                  self.debugPrint("Data fetched from API successfully")
                  return data
              else:
                  self.debugPrint(f"Error fetching NHL goaltending GAA leaders: {response.status_code}")
                  return None
          except Exception as e:
              self.debugPrint(f"Exception occurred while fetching NHL goaltending GAA leaders: {e}")
              return None
      def compile_nhl_goaltending_gaa_leaders(self, request:data_request=None)->list:
          try:
              self.debugPrint("Compiling data into list of "+ request.label)
              jsonDataList = request.jsonData
              retDataList = []
              counter = 0
              rows = len(jsonDataList['goalsAgainstAverage'])
              self.debugPrint("Number of goaltending GAA leaders: "+str(rows))
              for i in range(rows):
                  leader = jsonDataList['goalsAgainstAverage'][i]
                  nhlGoaltendingGaaLeader = nhl_goaltending_gaa_leader()
                  nhlGoaltendingGaaLeader.rank = i+1
                  nhlGoaltendingGaaLeader.first_name = leader['firstName']['default']
                  nhlGoaltendingGaaLeader.last_name = leader['lastName']['default']
                  nhlGoaltendingGaaLeader.team_name = leader['teamName']['default']
                  nhlGoaltendingGaaLeader.gaa = leader['value']
                  nhlGoaltendingGaaLeader.headshot_url = leader['headshot']
                  nhlGoaltendingGaaLeader.teamlogo_url = leader['teamLogo']
                  retDataList.append(nhlGoaltendingGaaLeader)
              self.debugPrint("Compiled " + request.label + " successfully")
              return retDataList
          except Exception as e:
              self.debugPrint("compile_nhl_goaltending_gaa_leaders - Error compiling " + request.label + ": " + str(e))
              return []
      def clear_nhl_goaltending_gaa_leaders_table_from_db(self, request:data_request=None)->bool:
          try:
              self.debugPrint("Clearing " + request.label + " from database")
              sqlQuery = '''delete from nhl_goaltending_gaa_leaders'''
              request.dbCursor.execute(sqlQuery)
              request.dbConn.commit()
              self.debugPrint(request.label + " cleared from database successfully")
          except Exception as e:
              self.debugPrint("Error clearing " + request.label + " from database: " + str(e))
              self.debugPrint("Error saving " + request.label + " to database: " + str(e))
              request.dbConn.rollback()
              self.debugPrint("Rolled back the transaction.")
              request.dbConn.close()
              self.debugPrint("Closed the database connection.")
              exit(1)
      def save_nhl_goaltending_gaa_leaders_to_db(self, request:data_request=None)->bool:
          try:
                modelData = request.entityData # self.compile_nhl_goaltending_gaa_leaders()
                self.debugPrint("Inserting " + request.label + " into database")
                for leader in modelData:
                    # insert data into database.
                    sqlQuery = '''insert into nhl_goaltending_gaa_leaders(rank,first_name,last_name,team_name,gaa,headshot_url,teamlogo_url)
                                values(?,?,?,?,?,?,?)'''
                    data = (leader.rank, leader.first_name, leader.last_name, leader.team_name, leader.gaa, leader.headshot_url, leader.teamlogo_url)
                    request.dbCursor.execute(sqlQuery, data)
                    self.debugPrint("Committing " + request.label + " to database")
                    request.dbConn.commit()
                return True
          except Exception as e:
                 self.debugPrint("save_nhl_goaltending_gaa_leaders_to_db - Error saving " + request.label + " to database: " + str(e))
                 request.dbConn.rollback()
                 self.debugPrint("Rolled back the transaction.")
                 request.dbConn.close()
                 self.debugPrint("Closed the database connection.")
                 exit(1)
      def process_nhl_goaltending_gaa_leaders(self)->bool:
          try:
                # create data table.
                processRequest = data_request()
                processRequest.dbCursor = self.dbCursor
                processRequest.dbConn = self.dbConn
                processRequest.label = "NHL Goaltending GAA Leaders"
                # create data table for nhl skating leaders.
                self.create_nhl_goaltending_gaa_leaders_table(processRequest)

                # get json data from api.
                processRequest.jsonData = self.get_nhl_goaltending_gaa_leaders_data()

                # clear existing data from database table.
                self.clear_nhl_goaltending_gaa_leaders_table_from_db(processRequest)

                # compile data into list of nhl_skate_leader objects.
                processRequest.entityData = self.compile_nhl_goaltending_gaa_leaders(processRequest)

                # save data to database.
                self.save_nhl_goaltending_gaa_leaders_to_db(processRequest)
                return True
          except Exception as e:
                 self.debugPrint("process_nhl_goaltending_gaa_leaders - Error processing " + processRequest.label + ": " + str(e))
                 return False
      # End - Get NHL Goaltending GAA Leaders
      #---------------------------------------------------

      #---------------------------------------------------
      # Start - Get NHL Goaltending Wins Leaders
      def create_nhl_goaltending_wins_leaders_table(self, request:data_request=None)->bool:
            try:
                self.debugPrint("Creating "+ request.label +" table in database")
                query = '''
                        CREATE TABLE IF NOT EXISTS nhl_goaltending_wins_leaders (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rank integer not null,
                            first_name text not null,
                            last_name text not null,
                            team_name text not null,
                            wins integer not null,
                            headshot_url text not null,
                            teamlogo_url text not null,
                            datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
                        );
                        '''
                     # Execute the SQL command
                request.dbCursor.execute(query)
                # Commit the changes
                request.dbConn.commit()
                self.debugPrint(request.label +" table created in database successfully")
                return True
            except sqlite3.OperationalError:
                     self.debugPrint("Error occurred while creating "+ request.label +" table.")
                     request.dbConn.rollback()
                     self.debugPrint("Rolled back the transaction.")
                     request.dbConn.close()
                     self.debugPrint("Closed the database connection.")
                     return False
      def get_nhl_goaltending_wins_leaders_data(self) ->any:
          try:
              self.debugPrint("Fetching data from API")
              url = "https://api-web.nhle.com/v1/goalie-stats-leaders/20252026/3?categories=wins&limit=5"
              response = requests.get(url)
              if response.status_code == 200:
                  data = response.json()
                  self.debugPrint("Data fetched from API successfully")
                  return data
              else:
                  self.debugPrint(f"Error fetching NHL goaltending wins leaders: {response.status_code}")
                  return None
          except Exception as e:
              self.debugPrint(f"Exception occurred while fetching NHL goaltending wins leaders: {e}")
              return None
      def compile_nhl_goaltending_wins_leaders(self, request:data_request=None)->list:
          try:
              self.debugPrint("Compiling data into list of "+ request.label)
              jsonDataList = request.jsonData
              retDataList = []
              counter = 0
              rows = len(jsonDataList['wins'])
              self.debugPrint("Number of goaltending wins leaders: "+str(rows))
              for i in range(rows):
                  leader = jsonDataList['wins'][i]
                  nhlGoaltendingWinsLeader = nhl_goaltending_win_leader()
                  nhlGoaltendingWinsLeader.rank = i+1
                  nhlGoaltendingWinsLeader.first_name = leader['firstName']['default']
                  nhlGoaltendingWinsLeader.last_name = leader['lastName']['default']
                  nhlGoaltendingWinsLeader.team_name = leader['teamName']['default']
                  nhlGoaltendingWinsLeader.wins = leader['value']
                  nhlGoaltendingWinsLeader.headshot_url = leader['headshot']
                  nhlGoaltendingWinsLeader.teamlogo_url = leader['teamLogo']
                  retDataList.append(nhlGoaltendingWinsLeader)
              self.debugPrint("Compiled " + request.label + " successfully")
              return retDataList
          except Exception as e:
              self.debugPrint("compile_nhl_goaltending_wins_leaders - Error compiling " + request.label + ": " + str(e))
              return []
      def clear_nhl_goaltending_wins_leaders_table_from_db(self, request:data_request=None)->bool:
          try:
              self.debugPrint("Clearing " + request.label + " from database")
              sqlQuery = '''delete from nhl_goaltending_wins_leaders'''
              request.dbCursor.execute(sqlQuery)
              request.dbConn.commit()
              self.debugPrint(request.label + " cleared from database successfully")
          except Exception as e:
              self.debugPrint("Error clearing " + request.label + " from database: " + str(e))
              self.debugPrint("Error saving " + request.label + " to database: " + str(e))
              request.dbConn.rollback()
              self.debugPrint("Rolled back the transaction.")
              request.dbConn.close()
              self.debugPrint("Closed the database connection.")
              exit(1)
      def save_nhl_goaltending_wins_leaders_to_db(self, request:data_request=None)->bool:
          try:
                modelData = request.entityData # self.compile_nhl_goaltending_wins_leaders()
                self.debugPrint("Inserting " + request.label + " into database")
                for leader in modelData:
                    # insert data into database.
                    sqlQuery = '''insert into nhl_goaltending_wins_leaders(rank,first_name,last_name,team_name,wins,headshot_url,teamlogo_url)
                                values(?,?,?,?,?,?,?)'''
                    data = (leader.rank, leader.first_name, leader.last_name, leader.team_name, leader.wins, leader.headshot_url, leader.teamlogo_url)
                    request.dbCursor.execute(sqlQuery, data)
                    self.debugPrint("Committing " + request.label + " to database")
                    request.dbConn.commit()
                return True
          except Exception as e:
                 self.debugPrint("save_nhl_goaltending_wins_leaders_to_db - Error saving " + request.label + " to database: " + str(e))
                 request.dbConn.rollback()
                 self.debugPrint("Rolled back the transaction.")
                 request.dbConn.close()
                 self.debugPrint("Closed the database connection.")
                 exit(1)
      def process_nhl_goaltending_wins_leaders(self)->bool:
          try:
                # create data table.
                processRequest = data_request()
                processRequest.dbCursor = self.dbCursor
                processRequest.dbConn = self.dbConn
                processRequest.label = "NHL Goaltending Wins Leaders"
                # create data table for nhl skating leaders.
                self.create_nhl_goaltending_wins_leaders_table(processRequest)

                # get json data from api.
                processRequest.jsonData = self.get_nhl_goaltending_wins_leaders_data()

                # clear existing data from database table.
                self.clear_nhl_goaltending_wins_leaders_table_from_db(processRequest)

                # compile data into list of nhl_skate_leader objects.
                processRequest.entityData = self.compile_nhl_goaltending_wins_leaders(processRequest)

                # save data to database.
                self.save_nhl_goaltending_wins_leaders_to_db(processRequest)
                return True
          except Exception as e:
                 self.debugPrint("process_nhl_goaltending_wins_leaders - Error processing " + processRequest.label + ": " + str(e))
                 return False
      # End - Get NHL Goaltending Wins Leaders
      #---------------------------------------------------

      #---------------------------------------------------
      # Start - Get NHL Goaltending Wins Leaders
      def create_nhl_goaltending_savepct_leaders_table(self, request:data_request=None)->bool:
            try:
                self.debugPrint("Creating "+ request.label +" table in database")
                query = '''
                        CREATE TABLE IF NOT EXISTS nhl_goaltending_savepct_leaders (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rank integer not null,
                            first_name text not null,
                            last_name text not null,
                            team_name text not null,
                            save_percentage real not null,
                            headshot_url text not null,
                            teamlogo_url text not null,
                            datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
                        );
                        '''
                     # Execute the SQL command
                request.dbCursor.execute(query)
                # Commit the changes
                request.dbConn.commit()
                self.debugPrint(request.label +" table created in database successfully")
                return True
            except sqlite3.OperationalError:
                     self.debugPrint("Error occurred while creating "+ request.label +" table.")
                     request.dbConn.rollback()
                     self.debugPrint("Rolled back the transaction.")
                     request.dbConn.close()
                     self.debugPrint("Closed the database connection.")
                     return False
      def get_nhl_goaltending_savepct_leaders_data(self) ->any:
          try:
              self.debugPrint("Fetching data from API")
              url = "https://api-web.nhle.com/v1/goalie-stats-leaders/20252026/3?categories=savePctg&limit=5"
              response = requests.get(url)
              if response.status_code == 200:
                  data = response.json()
                  self.debugPrint("Data fetched from API successfully")
                  return data
              else:
                  self.debugPrint(f"Error fetching NHL goaltending save percentage leaders: {response.status_code}")
                  return None
          except Exception as e:
              self.debugPrint(f"Exception occurred while fetching NHL goaltending save percentage leaders: {e}")
              return None
      def compile_nhl_goaltending_savepct_leaders(self, request:data_request=None)->list:
          try:
              self.debugPrint("Compiling data into list of "+ request.label)
              jsonDataList = request.jsonData
              retDataList = []
              counter = 0
              rows = len(jsonDataList['savePctg'])
              self.debugPrint("Number of goaltending save percentage leaders: "+str(rows))
              for i in range(rows):
                  leader = jsonDataList['savePctg'][i]
                  nhlGoaltendingSavePctLeader = nhl_goaltending_save_pct_leader()
                  nhlGoaltendingSavePctLeader.rank = i+1
                  nhlGoaltendingSavePctLeader.first_name = leader['firstName']['default']
                  nhlGoaltendingSavePctLeader.last_name = leader['lastName']['default']
                  nhlGoaltendingSavePctLeader.team_name = leader['teamName']['default']
                  nhlGoaltendingSavePctLeader.save_percentage = leader['value']
                  nhlGoaltendingSavePctLeader.headshot_url = leader['headshot']
                  nhlGoaltendingSavePctLeader.teamlogo_url = leader['teamLogo']
                  retDataList.append(nhlGoaltendingSavePctLeader)
              self.debugPrint("Compiled " + request.label + " successfully")
              return retDataList
          except Exception as e:
              self.debugPrint("compile_nhl_goaltending_savepct_leaders - Error compiling " + request.label + ": " + str(e))
              return []
      def clear_nhl_goaltending_savepct_leaders_table_from_db(self, request:data_request=None)->bool:
          try:
              self.debugPrint("Clearing " + request.label + " from database")
              sqlQuery = '''delete from nhl_goaltending_savepct_leaders'''
              request.dbCursor.execute(sqlQuery)
              request.dbConn.commit()
              self.debugPrint(request.label + " cleared from database successfully")
          except Exception as e:
              self.debugPrint("Error clearing " + request.label + " from database: " + str(e))
              self.debugPrint("Error saving " + request.label + " to database: " + str(e))
              request.dbConn.rollback()
              self.debugPrint("Rolled back the transaction.")
              request.dbConn.close()
              self.debugPrint("Closed the database connection.")
              exit(1)
      def save_nhl_goaltending_savepct_leaders_to_db(self, request:data_request=None)->bool:
          try:
                modelData = request.entityData # self.compile_nhl_goaltending_wins_leaders()
                self.debugPrint("Inserting " + request.label + " into database")
                for leader in modelData:
                    # insert data into database.
                    sqlQuery = '''insert into nhl_goaltending_savepct_leaders(rank,first_name,last_name,team_name,save_percentage,headshot_url,teamlogo_url)
                                values(?,?,?,?,?,?,?)'''
                    data = (leader.rank, leader.first_name, leader.last_name, leader.team_name, leader.save_percentage, leader.headshot_url, leader.teamlogo_url)
                    request.dbCursor.execute(sqlQuery, data)
                    self.debugPrint("Committing " + request.label + " to database")
                    request.dbConn.commit()
                return True
          except Exception as e:
                 self.debugPrint("save_nhl_goaltending_savepct_leaders_to_db - Error saving " + request.label + " to database: " + str(e))
                 request.dbConn.rollback()
                 self.debugPrint("Rolled back the transaction.")
                 request.dbConn.close()
                 self.debugPrint("Closed the database connection.")
                 exit(1)
      def process_nhl_goaltending_savepct_leaders(self)->bool:
          try:
                # create data table.
                processRequest = data_request()
                processRequest.dbCursor = self.dbCursor
                processRequest.dbConn = self.dbConn
                processRequest.label = "NHL Goaltending Save Percentage Leaders"
                # create data table for nhl skating leaders.
                self.create_nhl_goaltending_savepct_leaders_table(processRequest)

                # get json data from api.
                processRequest.jsonData = self.get_nhl_goaltending_savepct_leaders_data()

                # clear existing data from database table.
                self.clear_nhl_goaltending_savepct_leaders_table_from_db(processRequest)

                # compile data into list of nhl_skate_leader objects.
                processRequest.entityData = self.compile_nhl_goaltending_savepct_leaders(processRequest)

                # save data to database.
                self.save_nhl_goaltending_savepct_leaders_to_db(processRequest)
                return True
          except Exception as e:
                 self.debugPrint("process_nhl_goaltending_savepct_leaders - Error processing " + processRequest.label + ": " + str(e))
                 return False
      # End - Get NHL Goaltending Wins Leaders
      #---------------------------------------------------

      #---------------------------------------------------
      # Start - Get NHL Skate Goals Leaders
      def create_nhl_skate_goal_leaders_table(self, request:data_request=None)->bool:
            try:
                self.debugPrint("Creating "+ request.label +" table in database")
                query = '''
                        CREATE TABLE IF NOT EXISTS nhl_skate_goal_leaders (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rank integer not null,
                            first_name text not null,
                            last_name text not null,
                            team_name text not null,
                            goals integer not null,
                            headshot_url text not null,
                            teamlogo_url text not null,
                            datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
                        );
                        '''
                     # Execute the SQL command
                request.dbCursor.execute(query)
                # Commit the changes
                request.dbConn.commit()
                self.debugPrint(request.label +" table created in database successfully")
                return True
            except sqlite3.OperationalError:
                     self.debugPrint("Error occurred while creating "+ request.label +" table.")
                     request.dbConn.rollback()
                     self.debugPrint("Rolled back the transaction.")
                     request.dbConn.close()
                     self.debugPrint("Closed the database connection.")
                     return False
      def get_nhl_skate_goal_leaders_data(self) ->any:
          try:
              self.debugPrint("Fetching data from API")
              url = "https://api-web.nhle.com/v1/skater-stats-leaders/20252026/3?categories=goals&limit=5"
              response = requests.get(url)
              if response.status_code == 200:
                  data = response.json()
                  self.debugPrint("Data fetched from API successfully")
                  return data
              else:
                  self.debugPrint(f"Error fetching NHL skate goal leaders: {response.status_code}")
                  return None
          except Exception as e:
              self.debugPrint(f"Exception occurred while fetching NHL skate goal leaders: {e}")
              return None
      def compile_nhl_skate_goal_leaders(self, request:data_request=None)->list:
          try:
              self.debugPrint("Compiling data into list of "+ request.label)
              jsonDataList = request.jsonData
              retDataList = []
              counter = 0
              rows = len(jsonDataList['goals'])
              self.debugPrint("Number of NHL skate goal leaders: "+str(rows))
              for i in range(rows):
                  leader = jsonDataList['goals'][i]
                  nhlSkateGoalLeader = nhl_skate_goal_leader()
                  nhlSkateGoalLeader.rank = i+1
                  nhlSkateGoalLeader.first_name = leader['firstName']['default']
                  nhlSkateGoalLeader.last_name = leader['lastName']['default']
                  nhlSkateGoalLeader.team_name = leader['teamName']['default']
                  nhlSkateGoalLeader.goals = leader['value']
                  nhlSkateGoalLeader.headshot_url = leader['headshot']
                  nhlSkateGoalLeader.teamlogo_url = leader['teamLogo']
                  retDataList.append(nhlSkateGoalLeader)
              self.debugPrint("Compiled " + request.label + " successfully")
              return retDataList
          except Exception as e:
              self.debugPrint("compile_nhl_skate_goal_leaders - Error compiling " + request.label + ": " + str(e))
              return []
      def clear_nhl_skate_goal_leaders_table_from_db(self, request:data_request=None)->bool:
          try:
              self.debugPrint("Clearing " + request.label + " from database")
              sqlQuery = '''delete from nhl_skate_goal_leaders'''
              request.dbCursor.execute(sqlQuery)
              request.dbConn.commit()
              self.debugPrint(request.label + " cleared from database successfully")
          except Exception as e:
              self.debugPrint("Error clearing " + request.label + " from database: " + str(e))
              self.debugPrint("Error saving " + request.label + " to database: " + str(e))
              request.dbConn.rollback()
              self.debugPrint("Rolled back the transaction.")
              request.dbConn.close()
              self.debugPrint("Closed the database connection.")
              exit(1)
      def save_nhl_skate_goal_leaders_to_db(self, request:data_request=None)->bool:
          try:
                modelData = request.entityData # self.compile_nhl_goaltending_wins_leaders()
                self.debugPrint("Inserting " + request.label + " into database")
                for leader in modelData:
                    # insert data into database.
                    sqlQuery = '''insert into nhl_skate_goal_leaders(rank,first_name,last_name,team_name,goals,headshot_url,teamlogo_url)
                                values(?,?,?,?,?,?,?)'''
                    data = (leader.rank, leader.first_name, leader.last_name, leader.team_name, leader.goals, leader.headshot_url, leader.teamlogo_url)
                    request.dbCursor.execute(sqlQuery, data)
                    self.debugPrint("Committing " + request.label + " to database")
                    request.dbConn.commit()
                return True
          except Exception as e:
                 self.debugPrint("save_nhl_skate_goal_leaders_to_db - Error saving " + request.label + " to database: " + str(e))
                 request.dbConn.rollback()
                 self.debugPrint("Rolled back the transaction.")
                 request.dbConn.close()
                 self.debugPrint("Closed the database connection.")
                 exit(1)
      def process_nhl_skate_goal_leaders(self)->bool:
          try:
                # create data table.
                processRequest = data_request()
                processRequest.dbCursor = self.dbCursor
                processRequest.dbConn = self.dbConn
                processRequest.label = "NHL Skate Goal Leaders"
                # create data table for nhl skate goal leaders.
                self.create_nhl_skate_goal_leaders_table(processRequest)

                # get json data from api.
                processRequest.jsonData = self.get_nhl_skate_goal_leaders_data()

                # clear existing data from database table.
                self.clear_nhl_skate_goal_leaders_table_from_db(processRequest)

                # compile data into list of nhl_skate_leader objects.
                processRequest.entityData = self.compile_nhl_skate_goal_leaders(processRequest)

                # save data to database.
                self.save_nhl_skate_goal_leaders_to_db(processRequest)
                return True
          except Exception as e:
                 self.debugPrint("process_nhl_skate_goal_leaders - Error processing " + processRequest.label + ": " + str(e))
                 return False
      # End - Get NHL Skate Goals Leaders
      #---------------------------------------------------

      def save_nhl_teams_to_db(self, dbCursor, dbConnection):
            try:
                self.debugPrint("Saving NHL Teams to database")
                sqlQuery = '''delete from nhl_teams'''
                dbCursor.execute(sqlQuery)
                dbConnection.commit()
                sqlQuery = '''
                    insert into nhl_teams(team_name, active)
                    select distinct a.team,1
                    from (
                          select home_team as team from nhl_scores
                          UNION
                          select away_team as team from nhl_scores
                         ) as a
                    order by team asc
                '''
                dbCursor.execute(sqlQuery)
                self.debugPrint("Commiting NHL Teams to database")
                dbConnection.commit()
                self.debugPrint("NHL Teams saved to database successfully")
                return True
            except Exception as e:
                     self.debugPrint("Error saving NHL Teams to database: " + str(e))
                     dbConnection.rollback()
                     self.debugPrint("Rolled back the transaction.")
                     dbConnection.close()
                     self.debugPrint("Closed the database connection.")
                     return False
      def import_nhl_scores(self,dbCursor, dbConnection):
          self.debugPrint("Importing NHL Scores into database")
          return self.save_nhl_scores_to_db(dbCursor, dbConnection)
          print("NHL Scores import complete")
      def copy_db_file(self, source_path, destination_path):
          try:
              with open(source_path, 'rb') as src_file:
                  with open(destination_path, 'wb') as dest_file:
                      dest_file.write(src_file.read())
              self.debugPrint(f"Database file copied from {source_path} to {destination_path}")
              return True
          except Exception as e:
              self.debugPrint(f"Error copying database file: {e}")
              return False

etl = NHLDataManager('./src/data/hockeyplayoffdb/hockeyplayoff.db', True)
etl.run_nhl_etl_process(True)
db_path = Path(__file__).resolve().parent.parent.parent  / "api" / "hockeyplayoffapi" / "data" / "hockeyplayoff.db"
etl.copy_db_file('./src/data/hockeyplayoffdb/hockeyplayoff.db', db_path)
