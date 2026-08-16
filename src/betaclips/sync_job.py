from dataclasses import dataclass


@dataclass
class SyncJob:
    """Defines a specific query that needs to be synced from database
    source to one sheet destination"""
    name: str
    query: str
    spreadsheet_id: str
    sheet_name: str
