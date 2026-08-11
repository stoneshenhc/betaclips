# A SyncJob represents a specific query that needs to be piped from one source to one destination
from .snowflake_client import SnowflakeClient
from .sheets_client import SheetsClient

class SyncJob:

    def __init__(self, query, spreadsheetid):

        self.query = query
        self.spreadsheetid = spreadsheetid
        self.sheetname = 'Sheet1'

    def execute() -> None:

        sfc = SnowflakeClient()
        df = sfc.query(self.query)
        sfc.close()

        gsc = SheetsClient()
        gsc.clear(spreadsheetid=self.spreadsheetid, sheetname=self.sheetname)
        gsc.write(spreadsheetid=self.spreadsheetid, sheetname=self.sheetname, dataframe=df)
