import sqlite3

class nhl_db_manager:
    _conn = None
    _cursor = None
    def __init__(self, connection):
        self._conn = connection
        self._cursor = self._conn.cursor()
    
    def execute_query(self, query: str, **kwargs)-> bool:
        try:
            if kwargs:
                self._cursor.execute(query, kwargs)
            else:
                self._cursor.execute(query)
            self._conn.commit()
            return True
        except Exception as e:
            raise Exception(f"An error occurred while executing the query: {e}")
            return False    
    
    def execute_fetch(self, query: str, **kwargs)-> any:
        try:
            if kwargs:
                self._cursor.execute(query, kwargs)
            else:
                self._cursor.execute(query)
            return self._cursor.fetchall()
        except Exception as e:
            raise Exception(f"An error occurred while executing the fetch query: {e}")