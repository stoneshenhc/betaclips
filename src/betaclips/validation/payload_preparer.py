import json

from betaclips.constants import MAX_PAYLOAD_SIZE, MAX_CELLS, MAX_COLUMNS
from betaclips.exceptions import QueryTooLargeError


class PayloadPreparer:
    """For prepping the data to be written into the google sheet. Mainly
    handles size constraints."""

    # TODO: Turn into static methods or into a class-less module
    def estimated_size(self, values: list[list]) -> int:
        return len(json.dumps({'values': values}).encode('utf-8'))

    def column_count(self, values: list[list]) -> int:
        return len(values[0])

    def row_count(self, values: list[list]) -> int:
        return len(values)

    def check_sheet_limits(self, values: list[list]) -> None:
        rows = self.row_count(values)
        columns = self.column_count(values)
        if rows * columns > MAX_CELLS or columns > MAX_COLUMNS:
            raise QueryTooLargeError(rows, columns)

    def prepare(self, values: list[list]) -> list[list[list]]:
        rows = self.row_count(values)
        batch_loads = []
        # same as ceiling
        batches = int(
            -(-self.estimated_size(values) // (0.8 * MAX_PAYLOAD_SIZE))
        )
        batch_size = -(-rows // batches)
        for i in range(batches):
            batch_loads.append(values[i*batch_size:(i+1)*batch_size])
        return batch_loads
