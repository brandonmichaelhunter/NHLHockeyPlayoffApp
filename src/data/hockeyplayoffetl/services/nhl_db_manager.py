from typing import Any
from shared.db.factory import get_db_manager


class nhl_db_manager:
    """Compatibility shim that delegates to the shared SQLModelDBManager.

    dotenv files are loaded at construction so callers can choose `APP_ENV`.
    """

    def __init__(self, app_env: str | None = None):

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
