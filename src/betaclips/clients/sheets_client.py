from datetime import datetime, timezone

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from betaclips.validation.payload_preparer import PayloadPreparer
from betaclips.exceptions import (
    SpreadsheetNotFoundError,
    SheetNotFoundError,
    SpreadsheetPermissionError,
    SheetWriteError,
)


class SheetsClient:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = './credentials/betaclips-service-account.json'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
        creds = Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE,
            scopes=self.SCOPES,
        )
        self.service = build('sheets', 'v4', credentials=creds)

    def write(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        dataframe: pd.DataFrame,
        mode: str = 'overwrite',
    ) -> tuple[int, int, int]:
        sheet_id = self._get_sheet_id(spreadsheet_id, sheet_name)

        values = [dataframe.columns.tolist()] + dataframe.values.tolist()
        # TODO: make this just helper functions, not a class
        preparer = PayloadPreparer()
        preparer.check_sheet_limits(values)
        batches = preparer.prepare(values)
        row_counter = 1
        updated_rows = updated_cols = batch_counter = 0

        self.clear(spreadsheet_id, sheet_name)
        for batch in batches:
            try:
                result = self.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"'{sheet_name}'!A{row_counter}",
                    valueInputOption='USER_ENTERED',
                    body={'values': batch},
                ).execute(num_retries=5)
            except HttpError as error:
                if int(error.resp.status) == 400:
                    raise SheetWriteError(
                        spreadsheet_id, sheet_name, error._get_reason()
                    )
                raise error
            updated_rows += result.get('updatedRows', 0)
            updated_cols = max(updated_cols, result.get('updatedColumns', 0))
            batch_counter += 1
            row_counter += len(batch)

        now_utc = datetime.now(timezone.utc).strftime(self.DATETIME_FORMAT)
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=self._bold_and_note(sheet_id, f"Last synced: {now_utc} UTC"),
        ).execute()

        return (updated_rows, updated_cols, batch_counter)

    def clear(self, spreadsheet_id: str, sheet_name: str) -> None:
        try:
            self.service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=f"'{sheet_name}'",
                body={},
            ).execute(num_retries=3)
        except HttpError as error:
            if int(error.resp.status) == 403:
                raise SpreadsheetPermissionError(spreadsheet_id)
            raise error

    def _get_sheet_id(self, spreadsheet_id: str, sheet_name: str) -> int:
        try:
            metadata = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id,
                fields='sheets.properties',
            ).execute(num_retries=3)
        except HttpError as error:
            if int(error.resp.status == 404):
                raise SpreadsheetNotFoundError(spreadsheet_id)
            raise error

        for sheet in metadata.get('sheets', []):
            properties = sheet.get('properties', {})
            if properties.get('title') == sheet_name:
                return properties.get('sheetId')

        raise SheetNotFoundError(spreadsheet_id, sheet_name)

    def _bold_and_note(self, sheet_id: int, note: str) -> dict:
        body = {
            'requests': [
                {
                    'repeatCell': {

                        'range': {
                            'sheetId': sheet_id,
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
                            'sheetId': sheet_id,
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
