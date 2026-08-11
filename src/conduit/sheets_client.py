import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
# import google python client

# Start with service account or self account credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = './credentials/betaclips-service-account.json'

class SheetsClient:

    def __init__(self):

        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)

    # update to use dataframe later
    def write(self, sheetid : str, rangename : str, data : list, mode : str = 'overwrite') -> None:

        result = self.service.spreadsheets().values().update(
            spreadsheetId=sheetid,
            range=rangename,
            valueInputOption='USER_ENTERED',
            body={'values':data}
        ).execute()

        print(f"{result.get('updatedCells')} cells updated.")

        # handle writing, maybe in batches

    def clear(self, sheetid: str) -> None:
        pass
        # handle wiping entire sheet

    def newsheet(self, spreadsheetid: str) -> str:
        pass 
        # handle creating new sheet in spreadsheet and returning id

