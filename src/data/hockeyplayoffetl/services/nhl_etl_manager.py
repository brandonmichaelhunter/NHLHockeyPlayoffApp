
from datetime import timedelta
from datetime import date
from typing import Optional, Union
import sqlite3

from dns import query
# pyrefly: ignore [untyped-import]
from requests import models
import datetime
#from src.data.hockeyplayoffetl.models.nhl_models import DynamicObject, game, gameboxscore, nhl_team, player, playergamestats, season, teamroster,nhl_goaltending_win_leader
from ..models.nhl_models import DynamicObject, game,nhl_game_score, gameboxscore, nhl_team, player, playergamestats, season, teamroster,nhl_goaltending_win_leader
from .nhl_api_client import nhl_api_client
from .nhl_db_manager import nhl_db_manager
from ..utils.utility_manager import utility_manager
from ..models.api_url_models import api_url_request, api_url_response
class nhl_etl_manager:
    # pyrefly: ignore [bad-assignment]
    _apiClient: Optional[nhl_api_client]# Optional[nhl_api_client] = None
    _dbManager: Optional[nhl_db_manager]
    _displayConsoleLogs: bool = True
    _logWrapper: Optional[utility_manager]
    # pyrefly: ignore [not-a-type]
    _log: Union[any, None]
    def __init__(self, apiClient, dbManager, displayConsoleLogs: bool = True):
        self._displayConsoleLogs = displayConsoleLogs
        self._apiClient = apiClient
        self._dbManager = dbManager
        self._logWrapper = utility_manager("nhl_etl_manager","nhl_etl_manager.log",10,self._displayConsoleLogs)
        self._log = self._logWrapper.get_logger()

    def provision_app_tables(self):
        try:
            query_methods = [
                self.__get_teams_query,
                self.__get_team_roster_query,
                self.__get_game_box_score_query,
                self.__get_game_stats_query,
                self.__get_games_query,
                self.__get_players_query,
                self.__get_seasons_query,
                self.__get_player_game_stats_query,
                self.__get_goalie_wins_leaders_query,
                self.__get_nhl_scores_query
            ]
            for method in query_methods:
                query = method()
                table_name = method.__name__.replace('__get_', '').replace('_query', '')
                self._log.info(f"Creating table: {table_name}...")

                result = self._dbManager.execute_query(query)
                if not result:
                    self._log.error(f"Failed to create table: {table_name}")
                    # Optionally, you could raise an exception here
                else:
                    self._log.info(f"Table '{table_name}' created successfully or already exists.")


        except Exception as e:
            self._log.error(f"provision_app_tables: An error occurred while provisioning app tables: {e}")
            raise Exception(f"An error occurred while provisioning app tables: {e}")

    #---------------------------------
    def __get_teams_query(self) -> str:

        query = '''
            CREATE TABLE IF NOT EXISTS teams
            (
                id       integer NULL,
                franchise_id integer NULL,
                name     STRING  NULL,
                abbrv    STRING  NULL,
                logo_url STRING  NULL,
                city     TEXT    NULL,
                state    TEXT    NULL,
                country  TEXT    NULL,
                DateCreated DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            '''
        return query
    def __get_team_roster_query(self) -> str:
        query = '''
            CREATE TABLE IF NOT EXISTS team_roster
            (
                id                           integer  PRIMARY KEY AUTOINCREMENT NOT NULL,
                team_id                      integer  NULL    ,
                player_id                    INTEGER  NULL    ,
                start_date                   DateTime NULL    ,
                end_date                     DateTime NULL    ,
                jersey_number                integer  NULL    ,
                position                     text     NULL
            );
        '''
        return query
    def __get_game_box_score_query(self) -> str:
        query= '''
            CREATE TABLE IF NOT EXISTS game_box_scores
            (
                id            integer NOT NULL,
                game_id       integer NULL    ,
                period integer NULL    ,
                awayScore integer NULL    ,
                homeScore integer NULL    ,
                PRIMARY KEY (id AUTOINCREMENT)
            );
            '''
        return query
    def __get_game_stats_query(self) -> str:
        query = '''
            CREATE TABLE IF NOT EXISTS  game_stats
            (
            id                       integer NOT NULL,
            game_id                  integer NULL    ,
            player_id                integer NULL    ,
            goals                    integer NULL    ,
            saves                    integer NULL    ,
            shots_against            integer NULL    ,
            goals_against            integer NULL    ,
            plus_minus               integer NULL    ,
            assists                  integer NULL    ,
            total_penalities_minutes integer NULL    ,
            PRIMARY KEY (id AUTOINCREMENT)
            );
            '''
        return query
    def __get_player_game_stats_query(self) -> str:
        query = '''
            CREATE TABLE IF NOT EXISTS  player_game_stats
            (
                id                       integer NULL,
                gameID integer NULL,
                gameTypeID integer NULL,
                playerID integer NULL,
                position text NULL,
                goals integer NULL,
                assists integer NULL,
                points integer NULL,
                plusMinus integer NULL,
                pim integer NULL,
                hits integer NULL,
                powerPlayGoals integer NULL,
                faceoffWinningPctg integer NULL,
                blockedShots integer NULL,
                shifts integer NULL,
                evenStrengthShotsAgainst text NULL,
                powerPlayShotsAgainst text NULL,
                shorthandedShotsAgainst text NULL,
                saveShotsAgainst text NULL,
                savePctg integer NULL,
                evenStrengthGoalsAgainst integer NULL,
                powerPlayGoalsAgainst integer NULL,
                shorthandedGoalsAgainst integer NULL,
                goalsAgainst integer NULL,
                shotsAgainst integer NULL,
                saves integer NULL,
                toi text NULL,
                PRIMARY KEY (id AUTOINCREMENT)
            );
            '''
        return query
    def __get_games_query(self) -> str:
        query = '''
            CREATE TABLE IF NOT EXISTS games
            (
                id               integer  NOT NULL,
                gameDate     text  NULL    ,
                gameNumber     integer  NULL    ,
                gameScheduleStateId        integer  NULL    ,
                gameStateId    integer NULL    ,
                gameTypeId integer  NULL    ,
                homeScore integer  NULL    ,
                homeTeamId     integer     NULL    ,
                period     integer     NULL    ,
                seasonId   integer     NULL    ,
                visitingScore    integer     NULL    ,
                visitingTeamId  integer     NULL    ,
                year integer NULL,
                month integer NULL,
                day integer NULL,
                PRIMARY KEY (id)
            );
        '''
        return query
    def __get_players_query(self) -> str:
        query = '''
            CREATE TABLE IF NOT EXISTS players
            (
                id           INTEGER  NOT NULL,
                first_name   TEXT    NULL    ,
                m_initial    TEXT    NULL    ,
                last_name    TEXT    NULL    ,
                age          integer NULL    ,
                birth_place  Text    NULL    ,
                headshot_url Text    NULL

            );
        '''
        return query
    def __get_seasons_query(self) -> str:
        query = '''
            CREATE TABLE IF NOT EXISTS seasons
            (
                id                integer NOT NULL,
                start_season_year integer NULL    ,
                end_season_year   integer NULL
            );
        '''
        return query
    def __get_goalie_wins_leaders_query(self) -> str:
        query = '''
            CREATE TABLE IF NOT EXISTS goalie_wins_leaders
            (
                player_id                integer NOT NULL,
                team_id integer NULL    ,
                seasons   text NULL,
                first_name text NULL,
                last_name text NULL,
                team_name text NULL,
                team_abbrv text NULL,
                wins integer NULL,
                headshot_url text NULL,
                teamlogo_url text NULL
            );
        '''
        return query
    def __get_nhl_scores_query(self) -> str:
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
        return query
    #---------------------------------
    def register_api_urls(self)->list:
        try:
            api_urls = []
            api_urls.append(api_url_request(function_name="teams_info", endpoint_url="stats/rest/en/team"))
            api_urls.append(api_url_request(function_name="team_roster", endpoint_url="v1/roster/{team_abbrv}/current"))
            api_urls.append(api_url_request(function_name="player_info", endpoint_url="v1/player/{player_id}/landing"))
            api_urls.append(api_url_request(function_name="game_box_score", endpoint_url="v1/player/{player}/game-log/{season}/{game_type}"))
            api_urls.append(api_url_request(function_name="seasons", endpoint_url="v1/season"))

            return api_urls
        except Exception as e:
            self._log.error(f"register_api_urls: An error occurred while registering API URLs: {e}")
            raise Exception(f"An error occurred while registering API URLs: {e}")

    def run_data_extraction_process(self):
        try:
            #self.run_seasons_pipeline()
            #self.run_teams_pipeline()
            #self.run_team_roster_pipeline()
            #self.run_games_pipeline()
            #self.run_game_player_stats_pipeline()
            #self.run_game_box_score_pipeline()
            #self.run_goaltending_win_leaders_pipeline()
            self.run_nhl_scores_pipeline()
        except Exception as e:
            # pyrefly: ignore [missing-attribute]
            self._log.error(f"run_data_extraction_process: An error occurred while running the data extraction process: {e}")
            raise Exception(f"An error occurred while running the data extraction process: {e}")
    # ---------------------------------
    # Seasons Pipeline
    def run_seasons_pipeline(self):
        try:
            # extract season data from NHL API
            jsonData = self.extract_seasons_info()

            # transform json data into list of models
            models = self.transform_seasons_info(jsonData)

            # save model data to database
            self.load_seasons_info(models)

        except Exception as e:
            self._log.error(f"run_seasons_pipeline: An error occurred while running the seasons pipeline: {e}")
            raise Exception(f"An error occurred while running the seasons pipeline: {e}")
    def extract_seasons_info(self) -> list:
        try:
            extracted_data = self._apiClient.fetch_nhl_data(api_url_request(function_name="seasons", endpoint_url="v1/season").endpoint_url)
            return extracted_data
        except Exception as e:
            self._log.error(f"extract_seasons_info: An error occurred while extracting seasons info: {e}")
            raise Exception(f"An error occurred while extracting seasons info: {e}")
    def transform_seasons_info(self, extractedData: list) -> list:
        try:
            transformed_data = []
            for item in extractedData:
                id = item
                startYear = str(item)[0:4]
                endYear = str(item)[4:8]
                seasonModel = season(int(item), int(startYear), int(endYear))
                transformed_data.append(seasonModel)
            return transformed_data
        except Exception as e:
            self._log.error(f"transform_seasons_info: An error occurred while transforming seasons info: {e}")
            raise Exception(f"An error occurred while transforming seasons info: {e}")
    def load_seasons_info(self, transformedData: list):
        try:
            self.clear_table("seasons")
            for seasonModel in transformedData:
                print(seasonModel)
                query = '''
                    INSERT INTO seasons (id, start_season_year, end_season_year)
                    VALUES ({id}, {start_season_year}, {end_season_year});
                '''.format(id=seasonModel.id, start_season_year=seasonModel.startYear, end_season_year=seasonModel.endYear)
                result = self._dbManager.execute_query(query)
                if not result:
                    self._log.error(f"Failed to insert season data for season ID: {seasonModel.id}")
                    exit(1)
                else:
                    self._log.info(f"Season data inserted successfully for season ID: {seasonModel.id}")
        except Exception as e:
            self._log.error(f"load_seasons_info: An error occurred while loading seasons info: {e}")
            raise Exception(f"An error occurred while loading seasons info: {e}")
    # ----------------------------------
    # Teams Pipeline
    def run_teams_pipeline(self):
        try:
            # extract team data from NHL API
            jsonData = self.extract_teams_info()

            jsonTeamsFranchiseData = self.extract_team_franchise_info()

            # transform json data into list of models
            models = self.transform_teams_info(jsonData, jsonTeamsFranchiseData)

            # save model data to database
            self.load_teams_info(models)

        except Exception as e:
            self._log.error(f"run_teams_pipeline: An error occurred while running the teams pipeline: {e}")
            raise Exception(f"An error occurred while running the teams pipeline: {e}")

    def extract_teams_info(self) -> list:
        try:
            extracted_data = self._apiClient.fetch_nhl_data_with_url("https://api.nhle.com/stats/rest/en/team")
            return extracted_data
        except Exception as e:
            self._log.error(f"extract_teams_info: An error occurred while extracting teams info: {e}")
            raise Exception(f"An error occurred while extracting teams info: {e}")

    def extract_team_franchise_info(self) -> list:
        try:
            extracted_data = self._apiClient.fetch_nhl_data_with_url("https://api.nhle.com/stats/rest/en/franchise")
            return extracted_data
        except Exception as e:
            self._log.error(f"extract_team_franchise_info: An error occurred while extracting team franchise info: {e}")
            raise Exception(f"An error occurred while extracting team franchise info: {e}")

    def transform_teams_info(self, teamData: list, franchiseData: list) -> list:
        try:
            playoff_teams =self._dbManager.execute_fetch("SELECT team_name FROM nhl_teams;")
            playoff_francise_teams = []
            for playoff_team in playoff_teams:
                for item in franchiseData['data']:
                    franchise_id = item['id']
                    if(item['teamCommonName'] == playoff_team[0] ):
                        playoff_francise_teams.append(item)

            transformed_data = []
            for playoff_franchise_team in playoff_francise_teams:
                franchise_team_id = playoff_franchise_team['id']
                for item in teamData['data']:
                    if franchise_team_id == item['franchiseId'] and (item['fullName'] != "Quebec Nordiques" and
                                                                      item['fullName'] != "Hartford Whalers" and
                                                                      item['fullName'] != "Minnesota North Stars" and
                                                                      item['fullName'] != "Utah Hockey Club"):
                       id = item['id']
                       franchise_id = item['franchiseId']
                       name = item['fullName']
                       abbrv = item['triCode']
                       logoURL = f'https://assets.nhle.com/logos/nhl/svg/{abbrv}_light.svg'.format(abbrv=abbrv)
                       city = ''
                       state = ''
                       country = ''
                       teamModel = nhl_team(id, franchise_id, name, abbrv, logoURL, city, state, country)
                       transformed_data.append(teamModel)
            return transformed_data
        except Exception as e:
            self._log.error(f"transform_teams_info: An error occurred while transforming teams info: {e}")
            raise Exception(f"An error occurred while transforming teams info: {e}")

    def load_teams_info(self, transformedData: list):
        try:
            self.clear_table("teams")
            for teamModel in transformedData:
                print(teamModel)
                query = '''
                    INSERT INTO teams (id, franchise_id, name, abbrv, logo_url, city, state, country)
                    VALUES ({id}, {franchise_id}, '{name}', '{abbrv}', '{logoURL}', '{city}', '{state}', '{country}');
                '''.format(id=teamModel.id, franchise_id=teamModel.franchise_id, name=teamModel.name.replace("'", "''"), abbrv=teamModel.abbrv.replace("'", "''"), logoURL=teamModel.logoURL.replace("'", "''"), city=teamModel.city.replace("'", "''"), state=teamModel.state.replace("'", "''"), country=teamModel.country.replace("'", "''"))
                result = self._dbManager.execute_query(query)
                if not result:
                    self._log.error(f"Failed to insert team data for team ID: {teamModel.id}")
                    exit(1)
                else:
                    self._log.info(f"Team data inserted successfully for team ID: {teamModel.id}")
        except Exception as e:
            self._log.error(f"load_teams_info: An error occurred while loading teams info: {e}")
            raise Exception(f"An error occurred while loading teams info: {e}")
    #---------------------------------
    # Team Roster Pipeline
    def run_team_roster_pipeline(self):
        try:

            # extract team roster data from NHL API
            teamsInfo: list = self._dbManager.execute_fetch("SELECT abbrv, id FROM teams;")             # get list of team abbreviations from teams table.
            teamsRosters: list = []
            for team in teamsInfo:
                json_TeamRoster:list = self.extract_team_roster_info(team[0])
                teamRosterData = DynamicObject(abbrv=team[0], id=team[1], roster=json_TeamRoster)
                teamsRosters.append(teamRosterData)

            # transform json data into list of models
            models = self.transform_team_roster_info(teamsRosters)

            # save model data to database
            self.load_team_roster_info(models['teamPlayers'])
            self.load_players_info(models['players'])

        except Exception as e:
            self._log.error(f"run_team_roster_pipeline: An error occurred while running the team roster pipeline: {e}")
            raise Exception(f"An error occurred while running the team roster pipeline: {e}")

    def load_team_roster_info(self, transformedData: list):
        try:
            self.clear_table("team_roster")
            for teamRosterModel in transformedData:
                print(teamRosterModel)
                query = '''
                    INSERT INTO team_roster (team_id, player_id, start_date, end_date, jersey_number, position)
                    VALUES ({team_id}, {player_id}, '{start_date}', '{end_date}', {jersey_number}, '{position}');
                '''.format(team_id=teamRosterModel.teamID, player_id=teamRosterModel.playerID, start_date=teamRosterModel.startDate, end_date=teamRosterModel.endDate, jersey_number=teamRosterModel.jerseyNumber, position=teamRosterModel.position.replace("'", "''"))
                result = self._dbManager.execute_query(query)
                if not result:
                    self._log.error(f"Failed to insert team roster data for team ID: {teamRosterModel.teamID} and player ID: {teamRosterModel.playerID}")
                    exit(1)
                else:
                    self._log.info(f"Team roster data inserted successfully for team ID: {teamRosterModel.teamID} and player ID: {teamRosterModel.playerID}")
        except Exception as e:
            self._log.error(f"load_team_roster_info: An error occurred while loading team roster info: {e}")
            raise Exception(f"An error occurred while loading team roster info: {e}")

    def load_players_info(self, transformedData: list):
        try:
            self.clear_table("players")
            for playerModel in transformedData:
                print(playerModel)
                query = '''
                    INSERT INTO players (id, first_name, m_initial, last_name, age, birth_place, headshot_url)
                    VALUES ({id}, '{first_name}', '{m_initial}', '{last_name}', {age}, '{birth_place}', '{headshot_url}');
                '''.format(id=playerModel.id, first_name=playerModel.first_name.replace("'", "''"), m_initial='', last_name=playerModel.last_name.replace("'", "''"), age=0, birth_place=playerModel.birth_date.replace("'", "''"), headshot_url=playerModel.headshot_url.replace("'", "''"))
                result = self._dbManager.execute_query(query)
                if not result:
                    self._log.error(f"Failed to insert player data for player ID: {playerModel.id}")
                    exit(1)
                else:
                    self._log.info(f"Player data inserted successfully for player ID: {playerModel.id}")
        except Exception as e:
            self._log.error(f"load_players_info: An error occurred while loading players info: {e}")
            raise Exception(f"An error occurred while loading players info: {e}")

    def extract_team_roster_info(self, team_abbrv: str) -> list:
        try:
            extracted_data = self._apiClient.fetch_nhl_data(api_url_request(function_name="team_roster", endpoint_url=f"v1/roster/{team_abbrv}/current").endpoint_url)
            return extracted_data
        except Exception as e:
            self._log.error(f"extract_team_roster_info: An error occurred while extracting team roster info: {e}")
            raise Exception(f"An error occurred while extracting team roster info: {e}")

    def transform_team_roster_info(self, teamsRosters: list) -> dict:
        try:
            transformed_data = {}
            players = []
            teamPlayers = []
            for teamRoster in teamsRosters:
                teamID = teamRoster.id
                for playerRoster in teamRoster.roster['forwards']:

                    playerID = playerRoster['id']
                    first_name = playerRoster['firstName']['default']
                    last_name = playerRoster['lastName']['default']
                    m_inital = ''
                    birth_date = playerRoster['birthDate']
                    headshot_url = playerRoster['headshot']
                    print(f'{first_name} {last_name} - {teamRoster.abbrv}')
                    if 'sweaterNumber' in playerRoster and playerRoster['sweaterNumber'] is not None:
                        jerseyNumber = playerRoster['sweaterNumber']
                    else:
                        jerseyNumber = '0'
                    position = playerRoster['positionCode']
                    playerModel = player(playerID, first_name, m_inital, last_name, None, birth_date,headshot_url)
                    players.append(playerModel)
                    teamPlayerModel = teamroster(None, teamID, playerID, None, None, jerseyNumber, position)
                    teamPlayers.append(teamPlayerModel)

                for playerRoster in teamRoster.roster['defensemen']:
                    playerID = playerRoster['id']
                    first_name = playerRoster['firstName']['default']
                    m_inital = ''
                    last_name = playerRoster['lastName']['default']
                    birth_date = playerRoster['birthDate']
                    headshot_url = playerRoster['headshot']
                    if 'sweaterNumber' in playerRoster and playerRoster['sweaterNumber'] is not None:
                        jerseyNumber = playerRoster['sweaterNumber']
                    else:
                        jerseyNumber = '0'
                    position = playerRoster['positionCode']
                    playerModel = player(playerID, first_name, m_inital,  last_name, None, birth_date,headshot_url)
                    players.append(playerModel)
                    teamPlayerModel = teamroster(None, teamID, playerID, None, None, jerseyNumber, position)
                    teamPlayers.append(teamPlayerModel)

                for playerRoster in teamRoster.roster['goalies']:
                    playerID = playerRoster['id']
                    first_name = playerRoster['firstName']['default']
                    m_inital = ''
                    last_name = playerRoster['lastName']['default']
                    birth_date = playerRoster['birthDate']
                    headshot_url = playerRoster['headshot']
                    if 'sweaterNumber' in playerRoster and playerRoster['sweaterNumber'] is not None:
                        jerseyNumber = playerRoster['sweaterNumber']
                    else:
                        jerseyNumber = '0'
                    position = playerRoster['positionCode']
                    playerModel = player(playerID, first_name, m_inital,  last_name, None, birth_date,headshot_url)
                    players.append(playerModel)
                    teamPlayerModel = teamroster(None, teamID, playerID, None, None, jerseyNumber, position)
                    teamPlayers.append(teamPlayerModel)

            transformed_data = {"players": players, "teamPlayers": teamPlayers}
            return transformed_data
        except Exception as e:
            self._log.error(f"transform_team_roster_info: An error occurred while transforming team roster info: {e}")
            raise Exception(f"An error occurred while transforming team roster info: {e}")

    #---------------------------------
    # Games Pipeline
    def run_games_pipeline(self):
        try:
            # extract game data from NHL API
            jsonData = self.extract_games_info("https://api.nhle.com/stats/rest/en/game")

            # transform json data into list of models
            transformedData = self.transform_games_info(jsonData)

            # save model data to database
            self.load_games_info(transformedData)
        except Exception as e:
            self._log.error(f"run_games_pipeline: An error occurred while running the games pipeline: {e}")
            raise Exception(f"An error occurred while running the games pipeline: {e}")
    def extract_games_info(self, url:str ):
        try:
            extracted_data = self._apiClient.fetch_nhl_data_with_url(url)
            return extracted_data
        except Exception as e:
            self._log.error(f"extract_games_info: An error occurred while extracting games info: {e}")
            raise Exception(f"An error occurred while extracting games info: {e}")
    def transform_games_info(self, extractedData: list) -> list:
        try:
            transformed_data = []
            for item in extractedData['data']:
                id = item['id']
                gameDate = item['gameDate']
                gameNumber = item['gameNumber']
                gameScheduleStateId = item['gameScheduleStateId']
                gameStateId = item['gameStateId']
                gameTypeId = item['gameType']
                homeScore = item['homeScore']
                homeTeamId = item['homeTeamId']
                if 'period' in item and item['period'] is not None:
                    period = item['period']
                else:
                    period = 0
                seasonId = item['season']
                visitingScore = item['visitingScore']
                visitingTeamId = item['visitingTeamId']
                year = int(gameDate[0:4])
                month = int(gameDate[5:7])
                day = int(gameDate[8:10])
                gameModel = game(id, gameDate, gameNumber, gameScheduleStateId, gameStateId, gameTypeId, homeScore, homeTeamId, period, seasonId, visitingScore, visitingTeamId, year, month, day)
                transformed_data.append(gameModel)
            return transformed_data
        except Exception as e:
            self._log.error(f"transform_games_info: An error occurred while transforming games info: {e}")
            raise Exception(f"An error occurred while transforming games info: {e}")
    def load_games_info(self, transformedData: list):
        try:
            self.clear_table("games")
            for gameModel in transformedData:
                print(gameModel)
                query = '''
                    INSERT INTO games (id, gameDate, gameNumber, gameScheduleStateId, gameStateId, gameTypeId, homeScore, homeTeamId, period, seasonId, visitingScore, visitingTeamId, year, month, day)
                    VALUES ({id}, '{gameDate}', '{gameNumber}', '{gameScheduleStateId}', '{gameStateId}', '{gameTypeId}', {homeScore}, {homeTeamId}, {period}, {seasonId}, {visitingScore}, {visitingTeamId}, {year}, {month}, {day});
                '''.format(id=gameModel.id, gameDate=gameModel.gameDate.replace("'", "''"), gameNumber=gameModel.gameNumber, gameScheduleStateId=gameModel.gameScheduleStateId, gameStateId=gameModel.gameStateId, gameTypeId=gameModel.gameTypeId, homeScore=gameModel.homeScore, homeTeamId=gameModel.homeTeamId, period=gameModel.period, seasonId=gameModel.seasonId, visitingScore=gameModel.visitingScore, visitingTeamId=gameModel.visitingTeamId, year=gameModel.year, month=gameModel.month, day=gameModel.day)
                print(query)
                result = self._dbManager.execute_query(query)
                if not result:
                    self._log.error(f"Failed to insert game data for game ID: {gameModel.id}")
                    exit(1)
                else:
                    self._log.info(f"Game data inserted successfully for game ID: {gameModel.id}")

        except Exception as e:
            self._log.error(f"load_games_info: An error occurred while loading games info: {e}")
            raise Exception(f"An error occurred while loading games info: {e}")
    #---------------------------------
    # Game Player Stats Pipeline
    def run_game_player_stats_pipeline(self):
        try:
            current_year = self.__getCurrentYear()
            # get game ids from games table.
            game_ids = self._dbManager.execute_fetch(f"select id from games where year={current_year} and month in (4,5,6);")

            # extract game player stats data from NHL API
            jsonDataList = []
            for game_id in game_ids:
                jsonData = self.extract_game_player_stats_info(f"https://api-web.nhle.com/v1/gamecenter/{game_id[0]}/boxscore")
                if jsonData is not None:
                   jsonDataList.append(jsonData)
                else:
                    self._log.warning(f"No game player stats data found for game ID: {game_id[0]}")
            # transform json data into list of models
            transformedData = self.transform_game_player_stats_info(jsonDataList)

            # save model data to database
            self.load_game_player_stats_info(transformedData)
        except Exception as e:
            self._log.error(f"run_game_player_stats_pipeline: An error occurred while running the game player stats pipeline: {e}")
            raise Exception(f"An error occurred while running the game player stats pipeline: {e}")
    def extract_game_player_stats_info(self, url:str ):
        try:
            extracted_data = self._apiClient.fetch_nhl_data_with_url(url)
            return extracted_data
        except Exception as e:
            self._log.error(f"extract_game_player_stats_info: An error occurred while extracting game player stats info: {e}")
            raise Exception(f"An error occurred while extracting game player stats info: {e}")
    def transform_game_player_stats_info(self, games: list) -> list:
        try:
            transformed_data = []
            for game in games:
                gameTypeId = game['gameType']
                gameId = game['id']
                seasonId = game['season']
                #print(game['playerByGameStats']['awayTeam'])
                # for item in game['playerByGameStats']:
                if 'playerByGameStats' not in game or game['playerByGameStats'] is None:
                    self._log.warning(f"No player game stats data found for game ID: {gameId}")
                    continue
                print('away team - forwards')
                for awayTeam in game['playerByGameStats']['awayTeam']['forwards']:
                    playerId = awayTeam['playerId']
                    position = awayTeam['position']
                    goals = awayTeam['goals']
                    assists = awayTeam['assists']
                    points = awayTeam['points']
                    plusMinus = awayTeam['plusMinus']
                    pim = awayTeam['pim']
                    hits = awayTeam['hits']
                    powerPlayGoals = awayTeam['powerPlayGoals']
                    if 'faceoffWinningPctg' in awayTeam and awayTeam['faceoffWinningPctg'] is not None:
                        faceoffWinningPctg = awayTeam['faceoffWinningPctg']
                    else:
                        faceoffWinningPctg = 0
                    toi = awayTeam['toi']
                    blockedShots = awayTeam['blockedShots']
                    if 'shifts' in awayTeam and awayTeam['shifts'] is not None:
                        shifts = awayTeam['shifts']
                    else:
                        shifts = 0
                    playerGameStatsModel = playergamestats(
                        id=None,gameID=gameId,gameTypeID=gameTypeId,playerID=playerId,position=position,
                        goals=goals,assists=assists,points=points,plusMinus=plusMinus,pim=pim,hits=hits,
                        powerPlayGoals=powerPlayGoals,faceoffWinningPctg=faceoffWinningPctg,blockedShots=blockedShots,
                        shifts=shifts,evenStrengthShotsAgainst='',powerPlayShotsAgainst='',shorthandedShotsAgainst='',
                        saveShotsAgainst='',savePctg=0,evenStrengthGoalsAgainst=0,powerPlayGoalsAgainst=0,shorthandedGoalsAgainst=0,
                        goalsAgainst=0,shotsAgainst=0,saves=0,toi=toi)
                    transformed_data.append(playerGameStatsModel)
                print('away team - defense')
                for awayTeam in game['playerByGameStats']['awayTeam']['defense']:
                    playerId = awayTeam['playerId']
                    position = awayTeam['position']
                    goals = awayTeam['goals']
                    assists = awayTeam['assists']
                    points = awayTeam['points']
                    plusMinus = awayTeam['plusMinus']
                    pim = awayTeam['pim']
                    hits = awayTeam['hits']
                    powerPlayGoals = awayTeam['powerPlayGoals']
                    if 'faceoffWinningPctg' in awayTeam and awayTeam['faceoffWinningPctg'] is not None:
                        faceoffWinningPctg = awayTeam['faceoffWinningPctg']
                    else:
                        faceoffWinningPctg = 0
                    toi = awayTeam['toi']
                    blockedShots = awayTeam['blockedShots']

                    if 'shifts' in awayTeam and awayTeam['shifts'] is not None:
                        shifts = awayTeam['shifts']
                    else:
                        shifts = 0
                    playerGameStatsModel = playergamestats(
                        id=None,gameID=gameId,gameTypeID=gameTypeId,playerID=playerId,position=position,
                        goals=goals,assists=assists,points=points,plusMinus=plusMinus,pim=pim,hits=hits,
                        powerPlayGoals=powerPlayGoals,faceoffWinningPctg=faceoffWinningPctg,blockedShots=blockedShots,
                        shifts=shifts,evenStrengthShotsAgainst='',powerPlayShotsAgainst='',shorthandedShotsAgainst='',
                        saveShotsAgainst='',savePctg=0,evenStrengthGoalsAgainst=0,powerPlayGoalsAgainst=0,shorthandedGoalsAgainst=0,
                        goalsAgainst=0,shotsAgainst=0,saves=0,toi=toi)
                    transformed_data.append(playerGameStatsModel)
                print('away team - goalies')
                for awayTeam in game['playerByGameStats']['awayTeam']['goalies']:
                    playerId = awayTeam['playerId']
                    position = awayTeam['position']
                    evenStrengthShotsAgainst = awayTeam['evenStrengthShotsAgainst']
                    powerPlayShotsAgainst = awayTeam['powerPlayShotsAgainst']
                    shorthandedShotsAgainst = awayTeam['shorthandedShotsAgainst']
                    saveShotsAgainst = awayTeam['saveShotsAgainst']
                    if 'savePctg' in awayTeam and awayTeam['savePctg'] is not None:
                        savePctg = awayTeam['savePctg']
                    else:
                        savePctg = 0
                    evenStrengthGoalsAgainst = awayTeam['evenStrengthGoalsAgainst']
                    powerPlayGoalsAgainst = awayTeam['powerPlayGoalsAgainst']
                    shorthandedGoalsAgainst = awayTeam['shorthandedGoalsAgainst']
                    goalsAgainst = awayTeam['goalsAgainst']
                    shotsAgainst = awayTeam['shotsAgainst']
                    saves = awayTeam['saves']
                    #goals = awayTeam['goals']
                    toi = awayTeam['toi']
                    assists = 0
                    points = 0
                    plusMinus = 0
                    pim = 0
                    hits = 0
                    powerPlayGoals = 0
                    faceoffWinningPctg = 0
                    blockedShots = 0
                    shifts = 0
                    playerGameStatsModel = playergamestats(
                        id=None,gameID=gameId,gameTypeID=gameTypeId,playerID=playerId,position=position,
                        goals=goals,assists=assists,points=points,plusMinus=plusMinus,pim=pim,hits=hits,
                        powerPlayGoals=powerPlayGoals,faceoffWinningPctg=faceoffWinningPctg,blockedShots=blockedShots,
                        shifts=shifts,evenStrengthShotsAgainst=evenStrengthShotsAgainst,powerPlayShotsAgainst=powerPlayShotsAgainst,shorthandedShotsAgainst=shorthandedShotsAgainst,
                        saveShotsAgainst=saveShotsAgainst,savePctg=savePctg,evenStrengthGoalsAgainst=evenStrengthGoalsAgainst,powerPlayGoalsAgainst=powerPlayGoalsAgainst,shorthandedGoalsAgainst=shorthandedGoalsAgainst,
                        goalsAgainst=goalsAgainst,shotsAgainst=shotsAgainst,saves=saves,toi=toi)
                    transformed_data.append(playerGameStatsModel)
                print('home team - forwards')
                for homeTeam in game['playerByGameStats']['homeTeam']['forwards']:
                    playerId = homeTeam['playerId']
                    position = homeTeam['position']
                    goals = homeTeam['goals']
                    assists = homeTeam['assists']
                    points = homeTeam['points']
                    plusMinus = homeTeam['plusMinus']
                    pim = homeTeam['pim']
                    hits = homeTeam['hits']
                    powerPlayGoals = homeTeam['powerPlayGoals']
                    if 'faceoffWinningPctg' in homeTeam and homeTeam['faceoffWinningPctg'] is not None:
                        faceoffWinningPctg = homeTeam['faceoffWinningPctg']
                    else:
                        faceoffWinningPctg = 0
                    toi = homeTeam['toi']
                    blockedShots = homeTeam['blockedShots']
                    if 'shifts' in homeTeam and homeTeam['shifts'] is not None:
                        shifts = homeTeam['shifts']
                    else:
                        shifts = 0
                    playerGameStatsModel = playergamestats(
                        id=None,gameID=gameId,gameTypeID=gameTypeId,playerID=playerId,position=position,
                        goals=goals,assists=assists,points=points,plusMinus=plusMinus,pim=pim,hits=hits,
                        powerPlayGoals=powerPlayGoals,faceoffWinningPctg=faceoffWinningPctg,blockedShots=blockedShots,
                        shifts=shifts,evenStrengthShotsAgainst='',powerPlayShotsAgainst='',shorthandedShotsAgainst='',
                        saveShotsAgainst='',savePctg=0,evenStrengthGoalsAgainst=0,powerPlayGoalsAgainst=0,shorthandedGoalsAgainst=0,
                        goalsAgainst=0,shotsAgainst=0,saves=0,toi=toi)
                    transformed_data.append(playerGameStatsModel)
                print('home team - defense')
                for homeTeam in game['playerByGameStats']['homeTeam']['defense']:
                    playerId = homeTeam['playerId']
                    position = homeTeam['position']
                    goals = homeTeam['goals']
                    assists = homeTeam['assists']
                    points = homeTeam['points']
                    plusMinus = homeTeam['plusMinus']
                    pim = homeTeam['pim']
                    hits = homeTeam['hits']
                    powerPlayGoals = homeTeam['powerPlayGoals']
                    if 'faceoffWinningPctg' in homeTeam and homeTeam['faceoffWinningPctg'] is not None:
                        faceoffWinningPctg = homeTeam['faceoffWinningPctg']
                    else:
                        faceoffWinningPctg = 0
                    toi = homeTeam['toi']
                    blockedShots = homeTeam['blockedShots']
                    if 'shifts' in homeTeam and homeTeam['shifts'] is not None:
                        shifts = homeTeam['shifts']
                    else:
                        shifts = 0
                    playerGameStatsModel = playergamestats(
                        id=None,gameID=gameId,gameTypeID=gameTypeId,playerID=playerId,position=position,
                        goals=goals,assists=assists,points=points,plusMinus=plusMinus,pim=pim,hits=hits,
                        powerPlayGoals=powerPlayGoals,faceoffWinningPctg=faceoffWinningPctg,blockedShots=blockedShots,
                        shifts=shifts,evenStrengthShotsAgainst='',powerPlayShotsAgainst='',shorthandedShotsAgainst='',
                        saveShotsAgainst='',savePctg=0,evenStrengthGoalsAgainst=0,powerPlayGoalsAgainst=0,shorthandedGoalsAgainst=0,
                        goalsAgainst=0,shotsAgainst=0,saves=0,toi=toi)
                    transformed_data.append(playerGameStatsModel)
                print('home team - goalies')
                for homeTeam in game['playerByGameStats']['homeTeam']['goalies']:
                    playerId = homeTeam['playerId']
                    position = homeTeam['position']
                    evenStrengthShotsAgainst = homeTeam['evenStrengthShotsAgainst']
                    powerPlayShotsAgainst = homeTeam['powerPlayShotsAgainst']
                    shorthandedShotsAgainst = homeTeam['shorthandedShotsAgainst']
                    saveShotsAgainst = homeTeam['saveShotsAgainst']

                    if 'savePctg' in homeTeam and homeTeam['savePctg'] is not None:
                        savePctg = homeTeam['savePctg']
                    else:
                        savePctg = 0
                    evenStrengthGoalsAgainst = homeTeam['evenStrengthGoalsAgainst']
                    powerPlayGoalsAgainst = homeTeam['powerPlayGoalsAgainst']
                    shorthandedGoalsAgainst = homeTeam['shorthandedGoalsAgainst']
                    goalsAgainst = homeTeam['goalsAgainst']
                    shotsAgainst = homeTeam['shotsAgainst']
                    saves = homeTeam['saves']
                    goals = 0
                    toi = homeTeam['toi']
                    assists = 0
                    points = 0
                    plusMinus = 0
                    pim = 0
                    hits = 0
                    powerPlayGoals = 0
                    faceoffWinningPctg = 0
                    blockedShots = 0
                    shifts = 0
                    playerGameStatsModel = playergamestats(
                        id=None,gameID=gameId,gameTypeID=gameTypeId,playerID=playerId,position=position,
                        goals=goals,assists=assists,points=points,plusMinus=plusMinus,pim=pim,hits=hits,
                        powerPlayGoals=powerPlayGoals,faceoffWinningPctg=faceoffWinningPctg,blockedShots=blockedShots,
                        shifts=shifts,evenStrengthShotsAgainst=evenStrengthShotsAgainst,powerPlayShotsAgainst=powerPlayShotsAgainst,shorthandedShotsAgainst=shorthandedShotsAgainst,
                        saveShotsAgainst=saveShotsAgainst,savePctg=savePctg,evenStrengthGoalsAgainst=evenStrengthGoalsAgainst,powerPlayGoalsAgainst=powerPlayGoalsAgainst,shorthandedGoalsAgainst=shorthandedGoalsAgainst,
                        goalsAgainst=goalsAgainst,shotsAgainst=shotsAgainst,saves=saves,toi=toi)
                    transformed_data.append(playerGameStatsModel)

            return transformed_data
        except Exception as e:
            self._log.error(f"transform_game_player_stats_info: An error occurred while transforming game player stats info: {e}")
            raise Exception(f"An error occurred while transforming game player stats info: {e}")
    def load_game_player_stats_info(self, transformedData: list):
        try:
            self.clear_table("player_game_stats")
            for playerGameStatsModel in transformedData:
                print(playerGameStatsModel)
                query = '''
                    INSERT INTO player_game_stats (gameID, gameTypeID, playerID, position, goals, assists, points, plusMinus, pim, hits, powerPlayGoals, faceoffWinningPctg, blockedShots, shifts, evenStrengthShotsAgainst, powerPlayShotsAgainst, shorthandedShotsAgainst, saveShotsAgainst, savePctg, evenStrengthGoalsAgainst, powerPlayGoalsAgainst, shorthandedGoalsAgainst, goalsAgainst, shotsAgainst, saves, toi)
                    VALUES ({gameID}, {gameTypeID}, {playerID}, '{position}', {goals}, {assists}, {points}, {plusMinus}, {pim}, {hits}, {powerPlayGoals}, '{faceoffWinningPctg}', {blockedShots}, {shifts}, '{evenStrengthShotsAgainst}', '{powerPlayShotsAgainst}', '{shorthandedShotsAgainst}', '{saveShotsAgainst}', {savePctg}, {evenStrengthGoalsAgainst}, {powerPlayGoalsAgainst}, {shorthandedGoalsAgainst}, {goalsAgainst}, {shotsAgainst}, {saves}, '{toi}');
                '''.format(gameID=playerGameStatsModel.gameID, gameTypeID=playerGameStatsModel.gameTypeID, playerID=playerGameStatsModel.playerID, position=playerGameStatsModel.position.replace("'", "''"), goals=playerGameStatsModel.goals, assists=playerGameStatsModel.assists, points=playerGameStatsModel.points, plusMinus=playerGameStatsModel.plusMinus, pim=playerGameStatsModel.pim, hits=playerGameStatsModel.hits, powerPlayGoals=playerGameStatsModel.powerPlayGoals, faceoffWinningPctg=str(playerGameStatsModel.faceoffWinningPctg).replace("'", "''"), blockedShots=playerGameStatsModel.blockedShots, shifts=playerGameStatsModel.shifts, evenStrengthShotsAgainst=str(playerGameStatsModel.evenStrengthShotsAgainst).replace("'", "''"), powerPlayShotsAgainst=str(playerGameStatsModel.powerPlayShotsAgainst).replace("'", "''"), shorthandedShotsAgainst=str(playerGameStatsModel.shorthandedShotsAgainst).replace("'", "''"), saveShotsAgainst=str(playerGameStatsModel.saveShotsAgainst).replace("'", "''"), savePctg=playerGameStatsModel.savePctg, evenStrengthGoalsAgainst=playerGameStatsModel.evenStrengthGoalsAgainst, powerPlayGoalsAgainst=playerGameStatsModel.powerPlayGoalsAgainst, shorthandedGoalsAgainst=playerGameStatsModel.shorthandedGoalsAgainst, goalsAgainst=playerGameStatsModel.goalsAgainst, shotsAgainst=playerGameStatsModel.shotsAgainst, saves=playerGameStatsModel.saves, toi=playerGameStatsModel.toi.replace("'", "''"))
                result = self._dbManager.execute_query(query)
                if not result:
                    self._log.error(f"Failed to insert player game stats data for player ID: {playerGameStatsModel.playerID} and game ID: {playerGameStatsModel.gameID}")
                    exit(1)
                else:
                    self._log.info(f"Player game stats data inserted successfully for player ID: {playerGameStatsModel.playerID} and game ID: {playerGameStatsModel.gameID}")
        except Exception as e:
            self._log.error(f"load_game_player_stats_info: An error occurred while loading game player stats info: {e}")
            raise Exception(f"An error occurred while loading game player stats info: {e}")
    #---------------------------------

    #---------------------------------
    # Game Box Scores Pipeline
    def run_game_box_score_pipeline(self):
        try:
            # get game ids from games table.
            game_dates = self._dbManager.execute_fetch(f"select  distinct gameDate from games where year={self.__getCurrentYear()} and month in (4,5,6);")

            # extract game player stats data from NHL API
            jsonDataList = []
            for game_date in game_dates:
                jsonData = self.extract_game_box_scores_info(f"https://api-web.nhle.com/v1/score/{game_date[0]}")
                if jsonData is not None:
                   jsonDataList.append(jsonData)
                else:
                    self._log.warning(f"No game box scores data found for game date: {game_date[0]}")
            # transform json data into list of models
            transformedData = self.transform_game_box_scores_info(jsonDataList)

            # save model data to database
            self.load_game_box_scores_info(transformedData)
        except Exception as e:
            self._log.error(f"run_game_box_score_pipeline: An error occurred while running the game box scores pipeline: {e}")
            raise Exception(f"An error occurred while running the game box scores pipeline: {e}")

    def extract_game_box_scores_info(self, url:str ):
        try:
            extracted_data = self._apiClient.fetch_nhl_data_with_url(url)
            return extracted_data
        except Exception as e:
            self._log.error(f"extract_game_box_scores_info: An error occurred while extracting game box scores info: {e}")
            raise Exception(f"An error occurred while extracting game box scores info: {e}")

    def transform_game_box_scores_info(self, gameBoxScores: list) -> list:
        try:
            transformed_data = []
            for gameBoxScore in gameBoxScores:
                for game in gameBoxScore['games']:
                    gameId = game['id']
                    if 'goals' not in game or game['goals'] is None:
                        self._log.warning(f"No goals data found for game ID: {gameId}")
                        continue
                    for goal in game['goals']:
                        period = goal['period']
                        awayScore = goal['awayScore']
                        homeScore = goal['homeScore']
                        gameboxscoreModel = gameboxscore(id=None,gameID=gameId,period=period,awayScore=awayScore,homeScore=homeScore)
                        transformed_data.append(gameboxscoreModel)

            return transformed_data
        except Exception as e:
            self._log.error(f"transform_game_box_scores_info: An error occurred while transforming game box scores info: {e}")
            raise Exception(f"An error occurred while transforming game box scores info: {e}")

    def load_game_box_scores_info(self, transformedData: list):
        try:
            self.clear_table("game_box_scores")
            for gameboxscoreModel in transformedData:
                print(gameboxscoreModel)
                query = '''
                    INSERT INTO game_box_scores (game_id, period, awayScore, homeScore)
                    VALUES ({gameID}, {period}, {awayScore}, {homeScore});
                '''.format(gameID=gameboxscoreModel.gameID, period=gameboxscoreModel.period, awayScore=gameboxscoreModel.awayScore, homeScore=gameboxscoreModel.homeScore)
                result = self._dbManager.execute_query(query)
                if not result:
                    self._log.error(f"Failed to insert game box scores data for game ID: {gameboxscoreModel.gameID}")
                    exit(1)
                else:
                    self._log.info(f"Game box scores data inserted successfully for game ID: {gameboxscoreModel.gameID}")
        except Exception as e:
            self._log.error(f"load_game_box_scores_info: An error occurred while loading game box scores info: {e}")
            raise Exception(f"An error occurred while loading game box scores info: {e}")
    #---------------------------------
    # Goaltending Win Leaders Pipeline
    def run_goaltending_win_leaders_pipeline(self):
        try:
            current_year = self.__getCurrentYear()
            season = f"{current_year-1}{str(current_year)}"
            # extract goaltending win leaders data from NHL API
            jsonData = self.extract_goaltending_win_leaders_info(f"https://api-web.nhle.com/v1/goalie-stats-leaders/{season}/3?categories=wins&limit=100")

            # transform json data into list of models
            transformedData = self.transform_goaltending_win_leaders_info(jsonData)

            # save model data to database
            self.load_goaltending_win_leaders_info(transformedData)

        except Exception as e:
            self._log.error(f"run_goaltending_win_leaders_pipeline: An error occurred while running the goaltending win leaders pipeline: {e}")
            raise Exception(f"An error occurred while running the goaltending win leaders pipeline: {e}")

    def extract_goaltending_win_leaders_info(self, url:str ):
        try:
            extracted_data = self._apiClient.fetch_nhl_data_with_url(url)
            return extracted_data
        except Exception as e:
            self._log.error(f"extract_goaltending_win_leaders_info: An error occurred while extracting goaltending win leaders info: {e}")
            raise Exception(f"An error occurred while extracting goaltending win leaders info: {e}")

    def transform_goaltending_win_leaders_info(self, extractedData: list) -> list:
        try:
            transformed_data = []
            current_year = self.__getCurrentYear()
            currentSeason = f"{current_year-1}{str(current_year)}"
            # pyrefly: ignore [bad-index]
            for item in extractedData['wins']:
                playerID = item['id']
                season = currentSeason
                playerDetails = self.__getTeamPlayerDetails(playerID)
                print(playerDetails)
                first_name = playerDetails[0]
                last_name = playerDetails[1]
                headshot_url = playerDetails[2]
                team_name = playerDetails[3]
                team_abbrv = playerDetails[4]
                teamlogo_url = playerDetails[5]
                team_id = playerDetails[6]
                wins = item['value']
                goaltendingWinLeaderModel = nhl_goaltending_win_leader(player_id=playerID, team_id=team_id, seasons=season, first_name=first_name, last_name=last_name, team_name=team_name, team_abbrv=team_abbrv, wins=wins, headshot_url=headshot_url, teamlogo_url=teamlogo_url)
                transformed_data.append(goaltendingWinLeaderModel)

            return transformed_data
        except Exception as e:
            self._log.error(f"transform_goaltending_win_leaders_info: An error occurred while transforming goaltending win leaders info: {e}")
            raise Exception(f"An error occurred while transforming goaltending win leaders info: {e}")

    def load_goaltending_win_leaders_info(self, transformedData: list):
        try:
            self.clear_table("goalie_wins_leaders")
            for goaltendingWinLeaderModel in transformedData:
                print(goaltendingWinLeaderModel)
                query = '''
                    INSERT INTO goalie_wins_leaders (player_id, team_id, seasons, first_name, last_name, team_name, team_abbrv, wins, headshot_url, teamlogo_url)
                    VALUES ({player_id}, {team_id}, '{seasons}', '{first_name}', '{last_name}', '{team_name}', '{team_abbrv}', {wins}, '{headshot_url}', '{teamlogo_url}');
                '''.format(player_id=goaltendingWinLeaderModel.player_id, team_id=goaltendingWinLeaderModel.team_id, seasons=goaltendingWinLeaderModel.seasons, first_name=goaltendingWinLeaderModel.first_name.replace("'", "''"), last_name=goaltendingWinLeaderModel.last_name.replace("'", "''"), team_name=goaltendingWinLeaderModel.team_name.replace("'", "''"), team_abbrv=goaltendingWinLeaderModel.team_abbrv.replace("'", "''"), wins=goaltendingWinLeaderModel.wins, headshot_url=goaltendingWinLeaderModel.headshot_url.replace("'", "''"), teamlogo_url=goaltendingWinLeaderModel.teamlogo_url.replace("'", "''"))
                result = self._dbManager.execute_query(query)
                if not result:
                    self._log.error(f"Failed to insert goaltending win leader data for player: {goaltendingWinLeaderModel.first_name} {goaltendingWinLeaderModel.last_name}")
                    exit(1)
                else:
                    self._log.info(f"Goaltending win leader data inserted successfully for player: {goaltendingWinLeaderModel.first_name} {goaltendingWinLeaderModel.last_name}")
        except Exception as e:
            self._log.error(f"load_goaltending_win_leaders_info: An error occurred while loading goaltending win leaders info: {e}")
            raise Exception(f"An error occurred while loading goaltending win leaders info: {e}")

    # ---------------------------------
    # ---------------------------------
    # NHL Scores Pipeline
    def run_nhl_scores_pipeline(self):
        try:
            nhlGameDates = self.__getNHLPlayoffGameDates()
            nhlGameScores = []
            for nhlGameDate in nhlGameDates:
                jsonData = self.extract_nhl_scores_info(f"https://api-web.nhle.com/v1/score/{nhlGameDate}")
                if jsonData is not None:
                    nhlGameScores.append(jsonData)
                else:
                    self._log.warning(f"No NHL scores data found for game date: {nhlGameDate}")
            transformedData = self.transform_nhl_scores_info(nhlGameScores)
            self.load_nhl_scores_info(transformedData)
        except Exception as e:
            self._log.error(f"run_nhl_scores_pipeline: An error occurred while running the NHL scores pipeline: {e}")
            raise Exception(f"An error occurred while running the NHL scores pipeline: {e}")

    def extract_nhl_scores_info(self, url:str ):
        try:
            extracted_data = self._apiClient.fetch_nhl_data_with_url(url)
            return extracted_data
        except Exception as e:
            self._log.error(f"extract_nhl_scores_info: An error occurred while extracting NHL scores info: {e}")
            raise Exception(f"An error occurred while extracting NHL scores info: {e}")

    def transform_nhl_scores_info(self, GameBoxScores: list) -> list:
        try:
            transformed_data = []

            for gameBoxScore in GameBoxScores:
                if 'games' not in gameBoxScore or gameBoxScore['games'] is None:
                    print('No Game Object.')
                numberOfGames = len(gameBoxScore['games'])

                if numberOfGames > 0:
                    for i in range(numberOfGames):
                        game_score= nhl_game_score()
                        game_score.game_date = gameBoxScore['games'][i]['gameDate']
                        game_score.home_team = gameBoxScore['games'][i]['homeTeam']['name']['default']
                        game_score.home_team_image = gameBoxScore['games'][i]['homeTeam']['logo']
                        game_score.away_team = gameBoxScore['games'][i]['awayTeam']['name']['default']
                        game_score.away_team_image = gameBoxScore['games'][i]['awayTeam']['logo']

                        if('score' in gameBoxScore['games'][i]['homeTeam']):
                            game_score.home_score = gameBoxScore['games'][i]['homeTeam']['score']
                        else:
                            game_score.home_score = 0

                        if('score' in gameBoxScore['games'][i]['awayTeam']):
                            game_score.away_score = gameBoxScore['games'][i]['awayTeam']['score']
                        else:
                            game_score.away_score = 0

                        # Series info
                        game_score.round = gameBoxScore['games'][i]['seriesStatus']['round']
                        game_score.game_number = gameBoxScore['games'][i]['seriesStatus']['gameNumberOfSeries']
                        neededToWinSeries = gameBoxScore['games'][i]['seriesStatus']['neededToWin']
                        game_score.series_info = ""
                        topSeedWins = gameBoxScore['games'][i]['seriesStatus']['topSeedWins']
                        bottomSeedWins = gameBoxScore['games'][i]['seriesStatus']['bottomSeedWins']
                        topSeedName = gameBoxScore['games'][i]['seriesStatus']['topSeedTeamAbbrev']
                        bottomSeedName = gameBoxScore['games'][i]['seriesStatus']['bottomSeedTeamAbbrev']
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
                        goalsCount = len(gameBoxScore['games'][i]['goals'])
                        game_score.first_period_home_score = 0
                        game_score.first_period_away_score = 0
                        game_score.second_period_home_score = 0
                        game_score.second_period_away_score = 0
                        game_score.third_period_home_score = 0
                        game_score.third_period_away_score = 0
                        game_score.overtime_home_score = 0
                        game_score.overtime_away_score = 0
                        for goal in range(goalsCount):
                            goalItem = gameBoxScore['games'][i]['goals'][goal]
                            period = goalItem['period']
                            homeTeamAbbrv = gameBoxScore['games'][i]['homeTeam']['abbrev']
                            awayTeamAbbrv = gameBoxScore['games'][i]['awayTeam']['abbrev']
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
                        game_score.final_home_score = gameBoxScore['games'][i]['homeTeam']['score']
                        game_score.final_away_score = gameBoxScore['games'][i]['awayTeam']['score']
                        transformed_data.append(game_score)

            return transformed_data
        except Exception as e:
            self._log.error(f"transform_nhl_scores_info: An error occurred while transforming NHL scores info: {e}")
            raise Exception(f"An error occurred while transforming NHL scores info: {e}")
    def load_nhl_scores_info(self, transformedData: list[nhl_game_score]):
        try:
            self.clear_table("nhl_scores")
            for nhlScoreModel in transformedData:
                print(nhlScoreModel)
                query = '''
                    insert into nhl_scores(date,home_team,home_team_image,away_team,away_team_image,home_score,away_score,
                                              first_period_home_score,second_period_home_score,third_period_home_score,overtime_home_score,
                                              final_home_score,first_period_away_score,second_period_away_score,third_period_away_score,
                                              overtime_away_score,final_away_score,round,game_number,series_info)
                    VALUES ('{date}', '{home_team}', '{home_team_image}', '{away_team}', '{away_team_image}', {home_score}, {away_score},
                            {first_period_home_score}, {second_period_home_score}, {third_period_home_score}, {overtime_home_score},
                            {final_home_score}, {first_period_away_score}, {second_period_away_score}, {third_period_away_score},
                            {overtime_away_score}, {final_away_score}, '{round}', {game_number}, '{series_info}');
                '''.format(date=nhlScoreModel.game_date, home_team=nhlScoreModel.home_team.replace("'", "''"), home_team_image=nhlScoreModel.home_team_image.replace("'", "''"), away_team=nhlScoreModel.away_team.replace("'", "''"), away_team_image=nhlScoreModel.away_team_image.replace("'", "''"), home_score=nhlScoreModel.home_score, away_score=nhlScoreModel.away_score, first_period_home_score=nhlScoreModel.first_period_home_score, second_period_home_score=nhlScoreModel.second_period_home_score, third_period_home_score=nhlScoreModel.third_period_home_score, overtime_home_score=nhlScoreModel.overtime_home_score, final_home_score=nhlScoreModel.final_home_score, first_period_away_score=nhlScoreModel.first_period_away_score, second_period_away_score=nhlScoreModel.second_period_away_score, third_period_away_score=nhlScoreModel.third_period_away_score, overtime_away_score=nhlScoreModel.overtime_away_score, final_away_score=nhlScoreModel.final_away_score, round=nhlScoreModel.round, game_number=nhlScoreModel.game_number, series_info=nhlScoreModel.series_info.replace("'", "''"))
                result = self._dbManager.execute_query(query)
                if not result:
                    self._log.error(f"Failed to insert NHL score data for game: {nhlScoreModel.home_team} vs {nhlScoreModel.away_team} on {nhlScoreModel.game_date}")
                    exit(1)
                else:
                    self._log.info(f"NHL score data inserted successfully for game: {nhlScoreModel.home_team} vs {nhlScoreModel.away_team} on {nhlScoreModel.game_date}")
        except Exception as e:
            self._log.error(f"load_nhl_scores_info: An error occurred while loading NHL scores info: {e}")
            raise Exception(f"An error occurred while loading NHL scores info: {e}")

    # ---------------------------------
    # Helper Methods
    def clear_table(self, table_name: str = "seasons") -> bool:
        try:
            query = f"DELETE FROM {table_name};"
            result = self._dbManager.execute_query(query)
            if not result:
                self._log.error(f"Failed to clear {table_name} table.")
                exit(1)
            else:
                self._log.info(f"{table_name} table cleared successfully.")
                return True
        except Exception as e:
            self._log.error(f"clear_table: An error occurred while clearing {table_name} table: {e}")
            raise Exception(f"An error occurred while clearing {table_name} table: {e}")
    def __getCurrentYear(self):
        return datetime.datetime.now().year
    def __getTeamPlayerDetails(self, PlayerID: int) -> list:
        try:
            query =  f"""
                select player.first_name, player.last_name, player.headshot_url, team. name, team.abbrv, team.logo_url, team.id as team_id
                from team_roster teamRoster inner join players player on player.id = teamRoster.player_id
                                                                            inner join teams team on team.id = teamRoster.team_id
                where player_id = {PlayerID}
            """
            result = self._dbManager.execute_fetch(query)
            if not result:
                self._log.warning(f"No player details found for player ID: {PlayerID}")
                return None
            else:
                return result[0]
        except Exception as e:
            self._log.error(f"__getTeamPlayerDetails: An error occurred while fetching team and player details for player ID {PlayerID}: {e}")
            raise Exception(f"An error occurred while fetching team and player details for player ID {PlayerID}: {e}")
    def __getNHLPlayoffGameDates(self):
            #Target end date (inclusive)
            target_date = date(2026, 4, 18)
            # Current date
            current_date = date.today()- timedelta(days=1)

            # Ensure we are not asking for a future date
            if current_date < target_date:

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

            return date_list
