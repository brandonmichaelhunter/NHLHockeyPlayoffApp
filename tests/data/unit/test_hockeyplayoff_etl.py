import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from src.data.hockeyplayoffetl.hockeyplayoff_etl import NHLDataManager

# define test database initalization method.
@pytest.mark.unit
def test_init_test_db():
    with patch('sqlite3.connect') as mock_connect:
         mockConn = MagicMock()
         mockCursor = MagicMock()
         
         # configure return values
         mock_connect.return_value = mockConn
         mockConn.cursor.return_value = mockCursor
         
         dbMgr = NHLDataManager('test_db.db', False)
         
         
         # asserts
         assert dbMgr.dbConn == mockConn
         assert dbMgr.dbCursor == mockCursor
         mock_connect.assert_called_once_with('test_db.db')