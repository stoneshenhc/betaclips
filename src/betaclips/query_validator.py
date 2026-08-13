import snowflake.connector as sc
from .snowflake_client import SnowflakeClient

class QueryValidator:

    def __init__(self, sf_client: SnowflakeClient):
        self.sf_client = sf_client

    def validate(self, sql: str) -> dict:
        cursor = self.sf_client.conn.cursor()
        try:
            cursor.describe(sql)
            return {'valid':True, 'msg':None}
        except sc.errors.ProgrammingError as error:
            return {'valid':False, 'msg':error.msg}
        finally:
            cursor.close()
