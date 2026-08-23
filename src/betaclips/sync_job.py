from dataclasses import dataclass, fields


@dataclass
class SyncJob:
    """Defines a specific query that needs to be synced from database
    source to one sheet destination"""
    name: str
    sql: str
    spreadsheet_id: str
    sheet_name: str

    @classmethod
    def from_dict(cls, config_dict: dict):
        valid_fields = [field.name for field in fields(cls)]
        valid_dict = {key: value for key, value in config_dict.items() if key in valid_fields}
        return cls(**valid_dict)

