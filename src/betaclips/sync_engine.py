from betaclips.clients.snowflake_client import SnowflakeClient
from betaclips.clients.sheets_client import SheetsClient
from betaclips.sync_job import SyncJob
from betaclips.run_result import RunResult
from betaclips.exceptions import PartialWriteError, ExcessiveWriteError

class SyncEngine:

    def __init__(self, sf_client: SnowflakeClient, sheets_client: SheetsClient):
        self.sf_client = sf_client
        self.sheets_client = sheets_client

    def execute(self, job: SyncJob) -> None:
        df = self.sf_client.query(job.query)
        metadata = self.sheets_client.write(job.spreadsheetid, job.sheetname, df)
        if len(df) + 1 > metadata[0] or len(df.columns) > metadata[1]:
            raise PartialWriteError()
        elif len(df) + 1 < metadata[0] or len(df.columns) < metadata[1]:
            raise ExcessiveWriteError()
        return RunResult(job.name, 'success', metadata[0], metadata[1])

    def close(self):
        self.sf_client.close()
