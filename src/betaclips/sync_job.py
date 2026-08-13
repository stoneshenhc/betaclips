# A SyncJob represents a specific query that needs to be piped from one source to one destination
class SyncJob:

    def __init__(self, name, query, spreadsheetid, sheetname):
        self.name = name
        self.query = query
        self.spreadsheetid = spreadsheetid
        self.sheetname = sheetname

