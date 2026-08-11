import datetime as dt
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = './credentials/betaclips-service-account.json'

class SheetsClient:

    def __init__(self):

        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)

    def write(self, spreadsheetid: str, sheetname: str, dataframe: pd.DataFrame, mode: str = 'overwrite') -> None:

        sheetid = self._get_sheet_id(spreadsheetid, sheetname)

        values = [dataframe.columns.tolist()] + dataframe.values.tolist()
        result = self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheetid,
            range=f"{sheetname}!A1",
            valueInputOption='USER_ENTERED',
            body={'values':values}
        ).execute()

        print(f"{result.get('updatedCells')} cells updated.")

        now_utc = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheetid,
            body=self._bold_and_note(sheetid, f"Last synced: {now_utc} UTC")
        ).execute()

    def clear(self, spreadsheetid: str, sheetname: str) -> None:

        self.service.spreadsheets().values().clear(
            spreadsheetId=spreadsheetid,
            range=f"{sheetname}",
            body={}
        )

    def _get_sheet_id(self, spreadsheetid: str, sheetname: str) -> int:

        metadata = self.service.spreadsheets().get(
            spreadsheetId=spreadsheetid,
            fields='sheets.properties'
        ).execute()

        for sheet in metadata.get('sheets', []):
            properties = sheet.get('properties', {})
            if properties.get('title') == sheetname:
                return properties.get('sheetId')

        raise ValueError(f"Sheet '{sheetname}' not found in spreadsheet '{spreadsheetid}'.")

    def _bold_and_note(self, sheetid: int, note: str) -> dict:

        body = {
            'requests': [
                {
                    'repeatCell': {

                        'range': {
                            'sheetId': sheetid,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },

                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {
                                    'bold': True
                                }
                            }
                        },

                        'fields': 'userEnteredFormat.textFormat.bold'
                    }
                },

                {
                    'updateCells': {
                        'rows': {
                            'values': [{'note': note}]
                        },

                        'fields': 'note',

                        'range': {
                            'sheetId': sheetid,
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 1
                        }
                    }
                }
            ]
        }

        return body

