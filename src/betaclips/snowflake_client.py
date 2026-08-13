import os
import snowflake.connector as sc
import pandas as pd

class SnowflakeClient:

    def __init__(self):
        self.conn_params = {
            'account': os.environ['SNOWFLAKE_ACCOUNT'],
            'user': os.environ['SNOWFLAKE_USER'],
            'authenticator': 'SNOWFLAKE_JWT',
            'warehouse': os.environ['SNOWFLAKE_WAREHOUSE'],
            'database': os.environ['SNOWFLAKE_DATABASE'],
            'schema': os.environ['SNOWFLAKE_SCHEMA'],
            'role': os.environ['SNOWFLAKE_ROLE'],
            'private_key_file': os.environ['SNOWFLAKE_PRIVATE_KEY_PATH'],
            'private_key_file_pwd': os.environ['SNOWFLAKE_PRIVATE_KEY_PASSPHRASE']
        }
        self.conn = sc.connect(**self.conn_params)

    def query(self, sql: str) -> pd.DataFrame:
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetch_pandas_all()
        finally:
            cursor.close()

    def close(self) -> None:
        self.conn.close()
