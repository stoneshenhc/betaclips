from unittest.mock import Mock

import pytest

from betaclips.clients.snowflake_client import SnowflakeClient
from betaclips.exceptions import QueryTooLargeError


def test_query_result_too_many_cells():
    client = SnowflakeClient()
    conn_mock = Mock()
    client.conn = conn_mock
    conn_mock.cursor.return_value.rowcount = 100_000
    conn_mock.cursor.return_value.description = ['' for _ in range(1000)]
    
    with pytest.raises(QueryTooLargeError):
        client.query('SELECT 1')

def test_query_result_too_many_colums():
    client = SnowflakeClient()
    conn_mock = Mock()
    client.conn = conn_mock
    conn_mock.cursor.return_value.rowcount = 10
    conn_mock.cursor.return_value.description = ['' for _ in range(50000)]
    
    with pytest.raises(QueryTooLargeError):
        client.query('SELECT 1')
