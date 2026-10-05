import os
# import requests

# Adds the parent directory to the Python search path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3


from .services.nhl_api_client import nhl_api_client
from .services.nhl_etl_manager import nhl_etl_manager
from .services.nhl_db_manager import nhl_db_manager


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class NHLDataManager:
    dbConn = None
    dbCursor = None
    _dbFilePath = None
    _debugEnabled = False

    def __init__(self, _debugEnabled: bool = False):
        self._debugEnabled = _debugEnabled

    def run_nhl_etl_process(self, ProvisionTables: bool) -> bool:
        try:
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


if __name__ == "__main__":
    etl = NHLDataManager(True)
    etl.run_nhl_etl_process(True)
