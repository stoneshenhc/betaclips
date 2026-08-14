import os
import snowflake.connector as sc
import pandas as pd
from betaclips.validation.config_validation import validate_timeout

class SnowflakeClient:

    def __init__(self, statement_timeout: int | None = None):
        session_params = {}
        if statement_timeout is not None:
            timeout = validate_timeout(statement_timeout)
            session_params['STATEMENT_TIMEOUT_IN_SECONDS'] = timeout
        conn_params = {
            'account': os.environ['SNOWFLAKE_ACCOUNT'],
            'user': os.environ['SNOWFLAKE_USER'],
            'authenticator': 'SNOWFLAKE_JWT',
            'warehouse': os.environ['SNOWFLAKE_WAREHOUSE'],
            'database': os.environ['SNOWFLAKE_DATABASE'],
            'schema': os.environ['SNOWFLAKE_SCHEMA'],
            'role': os.environ['SNOWFLAKE_ROLE'],
            'private_key_file': os.environ['SNOWFLAKE_PRIVATE_KEY_PATH'],
            'private_key_file_pwd': os.environ['SNOWFLAKE_PRIVATE_KEY_PASSPHRASE'],
            'session_parameters': session_params
        }
        self.conn = sc.connect(**conn_params)

    def query(self, sql: str) -> pd.DataFrame:
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetch_pandas_all()
        finally:
            cursor.close()

    def close(self) -> None:
        self.conn.close()
