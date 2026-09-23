import os
# import requests

# Adds the parent directory to the Python search path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3


from .services.nhl_api_client import nhl_api_client
from .services.nhl_etl_manager import nhl_etl_manager
from .services.nhl_db_manager import nhl_db_manager

# try:
#     import tkinter as tk

#     print("Tkinter OK")
# except ImportError:
#     traceback.print_exc()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class NHLDataManager:
    dbConn = None
    dbCursor = None
    _dbFilePath = None
    _debugEnabled = False

    def __init__(self, DBFilePath: str, _debugEnabled: bool = False):
        self._dbFilePath = DBFilePath
        self._debugEnabled = _debugEnabled
        #self.debugPrint("Create connection to hockeyplayoffdb/hockeyplayoff.db")
        #self.dbConn = sqlite3.connect(self._dbFilePath)
        #self.debugPrint("Create cursor object to run sql commands against database")
        # create a cursor object to run sql commands against database.
        #self.debugPrint("Creating database cursor object.")
        #self.dbCursor = self.dbConn.cursor()
        #self.debugPrint("Database cursor object created.")

    def run_nhl_etl_process(self, ProvisionTables: bool) -> bool:
        try:
            # db_connection = sqlite3.connect(self._dbFilePath)
            # Initialize your managers
            self.debugPrint("Initializing NHL API Client, DB Manager, and ETL Manager.")
            api_client = nhl_api_client()
            db_manager = nhl_db_manager()
            etl_manager = nhl_etl_manager(api_client, db_manager, True)
            self.debugPrint("Managers initialized successfully.")
            if ProvisionTables:
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

    def debugPrint(self, message: str):
        if self._debugEnabled:
            print(message)

    # def closeDBConnection(self):
    #     self.debugPrint("Closing database connection.")
    #     self.dbConn.close()
    #     self.debugPrint("Database connection closed.")

    # def save_nhl_teams_to_db(self, dbCursor, dbConnection):
    #     try:
    #         self.debugPrint("Saving NHL Teams to database")
    #         sqlQuery = """delete from nhl_teams"""
    #         dbCursor.execute(sqlQuery)
    #         dbConnection.commit()
    #         sqlQuery = """
    #                 insert into nhl_teams(team_name, active)
    #                 select distinct a.team,1
    #                 from (
    #                       select home_team as team from nhl_scores
    #                       UNION
    #                       select away_team as team from nhl_scores
    #                      ) as a
    #                 order by team asc
    #             """
    #         dbCursor.execute(sqlQuery)
    #         self.debugPrint("Commiting NHL Teams to database")
    #         dbConnection.commit()
    #         self.debugPrint("NHL Teams saved to database successfully")
    #         return True
    #     except Exception as e:
    #         self.debugPrint("Error saving NHL Teams to database: " + str(e))
    #         dbConnection.rollback()
    #         self.debugPrint("Rolled back the transaction.")
    #         dbConnection.close()
    #         self.debugPrint("Closed the database connection.")
    #         return False

    # def import_nhl_scores(self, dbCursor, dbConnection):
    #     self.debugPrint("Importing NHL Scores into database")
    #     return self.save_nhl_scores_to_db(dbCursor, dbConnection)
    #     print("NHL Scores import complete")

    # def copy_db_file(self, source_path, destination_path):
    #     try:
    #         with open(source_path, "rb") as src_file:
    #             with open(destination_path, "wb") as dest_file:
    #                 dest_file.write(src_file.read())
    #         self.debugPrint(
    #             f"Database file copied from {source_path} to {destination_path}"
    #         )
    #         return True
    #     except Exception as e:
    #         self.debugPrint(f"Error copying database file: {e}")
    #         return False


if __name__ == "__main__":
    etl = NHLDataManager("./src/data/hockeyplayoffdb/hockeyplayoff.db", True)
    etl.run_nhl_etl_process(True)
