import os

import snowflake.connector as sc
import pandas as pd
from snowflake.connector.cursor import SnowflakeCursor

from betaclips.validation.validations import validate_timeout
from betaclips.exceptions import (
    QueryTimeoutError,
    QueryTooLargeError,
    SQLExecutionError,
)
from betaclips.constants import MAX_CELLS, MAX_COLUMNS


class SnowflakeClient:
    def __init__(self, statement_timeout: int | None = None):
        session_params = {}
        if statement_timeout is not None:
            self.statement_timeout = validate_timeout(statement_timeout)
            session_params['STATEMENT_TIMEOUT_IN_SECONDS'] = (
                self.statement_timeout
            )
        conn_params = {
            'account': os.environ['SNOWFLAKE_ACCOUNT'],
            'user': os.environ['SNOWFLAKE_USER'],
            'authenticator': 'SNOWFLAKE_JWT',
            'warehouse': os.environ['SNOWFLAKE_WAREHOUSE'],
            'database': os.environ['SNOWFLAKE_DATABASE'],
            'schema': os.environ['SNOWFLAKE_SCHEMA'],
            'role': os.environ['SNOWFLAKE_ROLE'],
            'secondary_roles': os.environ['SNOWFLAKE_SECONDARY_ROLES'],
            'private_key_file': os.environ['SNOWFLAKE_PRIVATE_KEY_PATH'],
            'private_key_file_pwd': (
                os.environ['SNOWFLAKE_PRIVATE_KEY_PASSPHRASE']
            ),
            'session_parameters': session_params
        }
        self.conn = sc.connect(**conn_params)

    def query(self, sql: str) -> pd.DataFrame:
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            self._check_result_shape(cursor)
            return cursor.fetch_pandas_all()
        except sc.errors.ProgrammingError as error:
            if error.errno == 630:
                raise QueryTimeoutError(self.statement_timeout)
            raise SQLExecutionError(error.msg)
        finally:
            cursor.close()

    @staticmethod
    def _check_result_shape(cursor: SnowflakeCursor) -> None:
        rows = cursor.rowcount
        columns = len(cursor.description)
        if rows * columns > MAX_CELLS or columns > MAX_COLUMNS:
            raise QueryTooLargeError(rows, columns)

    def close(self) -> None:
        self.conn.close()
