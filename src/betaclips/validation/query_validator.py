import snowflake.connector as sc

from betaclips.clients.snowflake_client import SnowflakeClient
from betaclips.validation.results import ValidationResult


class QueryValidator:
    def __init__(self, sf_client: SnowflakeClient):
        self.sf_client = sf_client

    def validate(self, sql: str) -> ValidationResult:
        cursor = self.sf_client.conn.cursor()
        try:
            cursor.describe(sql)
            return ValidationResult(True, None)
        except sc.errors.ProgrammingError as error:
            return ValidationResult(False, error.msg)
        finally:
            cursor.close()
