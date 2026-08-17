import logging

import snowflake.connector as sc
import pandas as pd
from snowflake.connector.cursor import SnowflakeCursor

from betaclips.exceptions import (
    QueryTimeoutError,
    QueryTooLargeError,
    SQLExecutionError,
)
from betaclips.constants import MAX_CELLS, MAX_COLUMNS

logger = logging.getLogger(__name__)


class SnowflakeClient:
    def __init__(self, **connect_kwargs):
        self.connect_kwargs = connect_kwargs
        self.conn = None

    def connect(self) -> None:
        self.conn = sc.connect(**self.connect_kwargs)
        logger.info(
            "Snowflake connection established: %s", 
            self.conn.session_id,
        )

    def query(self, sql: str) -> pd.DataFrame:
        cursor = self.conn.cursor() 
        try:
            logger.debug("Attempting to execute SQL statement: %s", sql)
            cursor.execute(sql)
            logger.info(
                "SQL statement successfully executed in session %s",
                self.conn.session_id,
            )
            self._check_result_shape(cursor)
            return cursor.fetch_pandas_all()
        except sc.errors.ProgrammingError as error:
            if error.errno == 630:
                timeout = self.connect_kwargs['session_parameters'][
                    'STATEMENT_TIMEOUT_IN_SECONDS'
                ]
                raise QueryTimeoutError(timeout)
            raise SQLExecutionError(error.msg)
        finally:
            cursor.close()

    @staticmethod
    def _check_result_shape(cursor: SnowflakeCursor) -> None:
        rows = cursor.rowcount
        columns = len(cursor.description)
        logger.info("Query results have %s rows %s columns", rows, columns)
        if rows * columns > MAX_CELLS or columns > MAX_COLUMNS:
            raise QueryTooLargeError(rows, columns)

    def close(self) -> None:
        self.conn.close()
        logger.info("Snowflake connection closed: %s", self.conn.session_id)
