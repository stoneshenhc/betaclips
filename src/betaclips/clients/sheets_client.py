import datetime as dt
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from betaclips.validation.payload_preparer import PayloadPreparer
from betaclips.exceptions import SpreadsheetNotFoundError, SheetNotFoundError, SpreadsheetPermissionError, SheetWriteError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = './credentials/betaclips-service-account.json'

class SheetsClient:

    def __init__(self):

        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)

    def write(self, spreadsheetid: str, sheetname: str, dataframe: pd.DataFrame, mode: str = 'overwrite') -> None:

        sheetid = self._get_sheet_id(spreadsheetid, sheetname)
        values = [dataframe.columns.tolist()] + dataframe.values.tolist()

        # TODO: consider taking this prep stage out of this class and into SyncEngine
        preparer = PayloadPreparer()
        preparer.check_sheet_limits(values)
        batches = preparer.prepare(values)

        row_counter = 1
        self.clear(spreadsheetid, sheetname)

        for batch in batches:
            try:
                result = self.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheetid,
                    range=f"'{sheetname}'!A{row_counter}",
                    valueInputOption='USER_ENTERED',
                    body={'values':batch}
                ).execute()
            except HttpError as error:
                if int(error.resp.status) == 400:
                    raise SheetWriteError(spreadsheetid, sheetname, error._get_reason())
                raise error
            print(f"{result.get('updatedCells')} cells updated.")
            row_counter += len(batch)
        now_utc = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheetid,
            body=self._bold_and_note(sheetid, f"Last synced: {now_utc} UTC")
        ).execute()

    def clear(self, spreadsheetid: str, sheetname: str) -> None:

        try:
            self.service.spreadsheets().values().clear(
                spreadsheetId=spreadsheetid,
                range=f"'{sheetname}'",
                body={}
            ).execute()
        except HttpError as error:
            if int(error.resp.status) == 403:
                raise SpreadsheetPermissionError(spreadsheetid)
            raise error

    def _get_sheet_id(self, spreadsheetid: str, sheetname: str) -> int:

        try:
            metadata = self.service.spreadsheets().get(
                spreadsheetId=spreadsheetid,
                fields='sheets.properties'
            ).execute()
        except HttpError as error:
            if int(error.resp.status == 404):
                raise SpreadsheetNotFoundError(spreadsheetid)
            raise error

        for sheet in metadata.get('sheets', []):
            properties = sheet.get('properties', {})
            if properties.get('title') == sheetname:
                return properties.get('sheetId')

        raise SheetNotFoundError(spreadsheetid, sheetname)

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

