import logging
import json

from betaclips.constants import MAX_PAYLOAD_SIZE, MAX_CELLS, MAX_COLUMNS
from betaclips.exceptions import QueryTooLargeError

logger = logging.getLogger(__name__)


def estimated_size(values: list[list]) -> int:
    """Size in bytes of serialized values that would be sent in request
    to Sheets API"""
    payload = json.dumps(
        {'values': values},
        separators=(',',':'),
    ).encode('utf-8')
    return len(payload)

def column_count(values: list[list]) -> int:
    return len(values[0])

def row_count(values: list[list]) -> int:
    return len(values)

def check_sheet_limits(values: list[list]) -> None:
    rows = row_count(values)
    columns = column_count(values)
    if rows * columns > MAX_CELLS or columns > MAX_COLUMNS:
        raise QueryTooLargeError(rows, columns)

def batch_values(values: list[list]) -> list[list[list]]:
    """Takes values and chunks them into smaller batches to match max payload.
    Returns batch of one if values are already smaller than max payload."""
    rows = row_count(values)
    size = estimated_size(values)
    logger.info(
        "Query result data has estimated serialized size of %s bytes",
        size
    )
    batch_loads = []
    # same as ceiling
    batches = int(-(-size // (0.8 * MAX_PAYLOAD_SIZE)))
    batch_size = -(-rows // batches)
    for i in range(batches):
        batch_loads.append(values[i*batch_size:(i+1)*batch_size])
    logger.info(
        "Query result data of %s rows was broken into %s batches",
        rows,
        batches
    )
    return batch_loads
