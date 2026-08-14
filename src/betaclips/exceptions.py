class BetaclipsError(Exception):
    """Base exception class for all errors that are specific to betaclips"""

class QueryTooLargeError(BetaclipsError):

    def __init__(self, rows: int | None, columns: int):
        self.rows = rows
        self.columns = columns
        super().__init__(f"Query result too large to sync. Result has {rows=} and {columns=}")

