from .snowflake_client import SnowflakeClient
from .sheets_client import SheetsClient
from .sync_job import SyncJob

class SyncEngine:

    def __init__(self, sf_client: SnowflakeClient, sheets_client: SheetsClient):
        self.sf_client = sf_client
        self.sheets_client = sheets_client

    def execute(self, job: SyncJob) -> None:
        df = self.sf_client.query(job.query)
        self.sheets_client.write(job.spreadsheetid, job.sheetname, df)

    def close(self):
        self.sf_client.close()
