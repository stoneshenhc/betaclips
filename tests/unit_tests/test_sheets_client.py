from unittest.mock import Mock

import pandas as pd
import pytest

from betaclips.clients.sheets_client import SheetsClient


def test_advancing_ranges_on_batch_write(monkeypatch):
    df = pd.DataFrame({'col1': [1, 2, 3, 4, 5], 'col2': [6, 7, 8, 9, 0]})
    fake_batches = [
        [['col1', 'col2'], [1, 6], [2, 7]],
        [[3, 8], [4, 9]],
        [[5, 0]]
    ]
    monkeypatch.setattr(
        'betaclips.clients.sheets_client.batch_values',
        lambda x: fake_batches,
    )
    client = SheetsClient(Mock())
    client._get_sheet_id = Mock(return_value=1)
    update_mock = client.service.spreadsheets.return_value.values.return_value.update
    update_mock.return_value.execute.side_effect = [
        {'updatedRows': 3, 'updatedColumns': 2},
        {'updatedRows': 2, 'updatedColumns': 2},
        {'updatedRows': 1, 'updatedColumns': 2},
    ]
    
    client.write('abc', 'Sheet1', df)
    ranges = [call.kwargs['range'] for call in update_mock.call_args_list]
    assert ranges == ["'Sheet1'!A1", "'Sheet1'!A4", "'Sheet1'!A6"] 

def test_bold_note_structure():
    body = SheetsClient._bold_and_note(3, 'Test note')
    assert body == {
        'requests': [
            {
                'repeatCell': {

                    'range': {
                        'sheetId': 3,
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
                        'values': [{'note': 'Test note'}]
                    },

                    'fields': 'note',

                    'range': {
                        'sheetId': 3,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 1
                    }
                }
            }
        ]
    }
