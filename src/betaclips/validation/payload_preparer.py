import json
from betaclips.validation.result import ValidationResult

class PayloadPreparer:

    # For prepping the data to be written into the google sheet. Mainly handles size constraints

    MAX_BYTE_SIZE = 50 * 1024 * 1024
    MAX_CELL_COUNT = 10000000
    MAX_COLUMN_COUNT = 18278

    def estimated_size(self, values: list[list]) -> int:
        return len(json.dumps({'values': values}).encode('utf-8'))

    def cell_count(self, values: list[list]) -> int:
        return self.column_count(values) * self.row_count(values)

    def column_count(self, values: list[list]) -> int:
        return len(values[0])

    def row_count(self, values: list[list]) -> int:
        return len(values)

    def exceed_sheet_limits(self, values: list[list]) -> ValidationResult:
        cells = self.cell_count(values)
        columns = self.column_count(values)
        if cells > self.MAX_CELL_COUNT or columns > self.MAX_COLUMN_COUNT:
            return ValidationResult(False, "Google Sheet cannot exceed 10M rows or 18,278 columns.")
        else:
            return ValidationResult(True, None)

    def prepare(self, values: list[list]) -> list[list[list]]:
        rows = self.row_count(values)
        batch_loads = []
        batches = int(-(-self.estimated_size(values) // (0.8 * self.MAX_BYTE_SIZE))) # same as ceiling
        batch_size = -(-rows // batches)
        for i in range(batches):
            batch_loads.append(values[i*batch_size:(i+1)*batch_size])

        # TODO: Do a quick row + column check on Snowflake side too before evening writing to dataframe for memory purposes
        return batch_loads


