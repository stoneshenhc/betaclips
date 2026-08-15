class BetaclipsError(Exception):
    """Base exception class for all errors that are specific to betaclips"""

class JobError(BetaclipsError):
    """Category for errors that are tied to a specific sync job"""

class QueryTimeoutError(JobError):
    """The query timed out before it could be completed."""

    def __init__(self, timeout: int):
        self.timeout = timeout
        super().__init__(f"Query timed out before completion. Timeout currently set at {timeout} seconds.")

class SQLExecutionError(JobError):
    """The query returned an error when attempting to execute the SQL. Usually a syntax or permission issue."""
    def __init__(self, error: str):
        self.error = error
        super().__init__(f"SQL execution error: {error}")

class QueryTooLargeError(JobError):
    """The dimension size of the query result exceeds the limits of what can be written into a Google Sheet"""

    def __init__(self, rows: int | None, columns: int):
        self.rows = rows
        self.columns = columns
        super().__init__(f"Query result too large to sync. Result has {rows=} and {columns=}.")

class SpreadsheetNotFoundError(JobError):
    """The Google Sheet file does not exist or could not be accessed."""
    
    def __init__(self, spreadsheetid: str):
        self.spreadsheetid = spreadsheetid
        super().__init__(f"The Google Sheet with id: {spreadsheetid} could not be accessed or does not exist.")

class SheetNotFoundError(JobError):
    """The specific tab within the Google Sheet does not exist."""
    
    def __init__(self, spreadsheetid:str, sheetname:str):
        self.spreadsheetid = spreadsheetid
        self.sheetname = sheetname
        super().__init__(f"The tab named \"{sheetname}\" within the spreadsheet with id: {spreadsheetid} does not exist.")

class SpreadsheetPermissionError(JobError):
    """The specific tab within the Google Sheet cannot be written into by the program."""

    def __init__(self, spreadsheetid: str):
        self.spreadsheetid = spreadsheetid
        super().__init__(f"The service account does not have editing access (but may have read access) to the spreadsheet with id: {spreadsheetid}.")

class SheetWriteError(JobError):
    """Writing of values into Google Sheet denied, likely because of malformed data or size limits"""

    def __init__(self, spreadsheetid: str, sheetname: str, reason: str):
        self.spreadsheetid = spreadsheetid
        self.reason = reason
        super().__init__(f"Data could not be written into {spreadsheetid=} {sheetname=}: {reason}")

class MismatchWriteError(JobError):
    """Different number of rows or columns written into Sheet than in query results"""

    def __init__(self, queried_rows: int, queried_cols: int, written_rows: int, written_cols: int):
        self.queried_rows = queried_rows
        self.queried_cols = queried_cols
        self.written_rows = written_rows
        self.written_cols = written_cols
        super().__init__(f"Query returned {queried_rows} rows x {queried_cols}. But {written_rows} x {written_cols} wrote to sheet.")

class PartialWriteError(MismatchWriteError):
    pass

class ExcessiveWriteError(MismatchWriteError):
    pass
     

