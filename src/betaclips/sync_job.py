class SyncJob:
    """Defines a specific query that needs to be synced from database source to one sheet destination"""

    def __init__(self, name, query, spreadsheetid, sheetname):
        self.name = name
        self.query = query
        self.spreadsheetid = spreadsheetid
        self.sheetname = sheetname

