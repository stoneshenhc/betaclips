class SyncJob:
    """Defines a specific query that needs to be synced from database
    source to one sheet destination"""

    def __init__(self, name, query, spreadsheet_id, sheet_name):
        self.name = name
        self.query = query
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
