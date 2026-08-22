import tomllib

import pandas as pd
import pytest

from betaclips.clients.snowflake_client import SnowflakeClient
from betaclips.exceptions import (
    QueryTimeoutError,
    SQLExecutionError,
)


def test_query_returns_correct_dataframe():
    with open('credentials/snowflake.toml', 'rb') as f:
        config = tomllib.load(f)
    conn_params = config['snowflake']
    client = SnowflakeClient(**conn_params)
    client.connect()
    sql = """
    SELECT *
    FROM (VALUES
      (1::NUMBER(3,0), 'Bob'::VARCHAR(50), 'Johnson'::VARCHAR(50)),
      (2, 'Jane', 'Doe')
    ) AS users(id, firstname, lastname);
    """
    df = client.query(sql)
    client.close()
    df_expected = pd.DataFrame({
        'ID': [1, 2],
        'FIRSTNAME': ['Bob', 'Jane'],
        'LASTNAME': ['Johnson', 'Doe'],
    })
    pd.testing.assert_frame_equal(df, df_expected, check_dtype=False)

def test_timeout_raises_timeout_error():
    with open('./credentials/snowflake.toml', 'rb') as f:
        config = tomllib.load(f)
    conn_params = config['snowflake']
    conn_params["session_parameters"] = {'statement_timeout_in_seconds': 2}
    client = SnowflakeClient(**conn_params)
    client.connect()
    with pytest.raises(QueryTimeoutError):
        client.query("SELECT SYSTEM$WAIT(5);")

def test_bad_query_raises_execution_error():
    with open('./credentials/snowflake.toml', 'rb') as f:
        config = tomllib.load(f)
    conn_params = config['snowflake']
    client = SnowflakeClient(**conn_params)
    client.connect()
    with pytest.raises(SQLExecutionError):
        client.query("SELECT * FROM doesnotexist;")
