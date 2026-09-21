import os
from pathlib import Path
from dotenv import load_dotenv  # type: ignore
from typing import Any
from shared.db.factory import get_db_manager

# Load environment files (keeps existing behavior for ETL runs)
ROOT_DIR = Path(__file__).resolve().parents[4]
APP_ENV = os.getenv("APP_ENV", "development")

load_dotenv(ROOT_DIR / ".env")
load_dotenv(ROOT_DIR / f".env.{APP_ENV}", override=True)


class nhl_db_manager:
    """Compatibility shim for the existing ETL API that delegates to the
    shared `SQLModelDBManager` implementation.

    This preserves the `execute_query` and `execute_fetch` methods used by ETL
    while centralizing DB engine configuration in `shared.db.factory`.
    """

    def __init__(self):
        # Create the shared SQLModel-backed DB manager using DATABASE_URL
        self._db = get_db_manager()

    def execute_query(self, query: str, **kwargs) -> bool:
        try:
            return self._db.execute_query(query, **kwargs)
        except Exception as e:
            raise Exception(f"An error occurred while executing the query: {e}")

    def execute_fetch(self, query: str, **kwargs) -> Any:
        try:
            return self._db.execute_fetch(query, **kwargs)
        except Exception as e:
            raise Exception(f"An error occurred while executing the fetch query: {e}")
