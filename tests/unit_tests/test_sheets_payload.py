import pytest
import random
from betaclips.clients.sheets_payload import (
    estimated_size,
    check_sheet_limits,
    batch_values,
)
from betaclips.exceptions import QueryTooLargeError


def test_known_serialized_size():
    values = [['a', 'b', 'c'], [0, 0, 0]]
    assert estimated_size(values) == 34

def test_serialized_size_grows():
    values = [['a', 'b', 'c'], [0, 0, 0]]
    values_plus = values + [[1, 1, 1]]
    assert estimated_size(values_plus) > estimated_size(values)

def test_serialized_size_handles_none():
    assert estimated_size(None) > 0

def test_column_limits():
    test_list = [['c' for _ in range(20000)], [0 for _ in range(20000)]]
    with pytest.raises(QueryTooLargeError):
        check_sheet_limits(test_list)

def test_cell_limits():
    test_list = [[0 for _ in range(1000)] for _ in range(11000)]
    with pytest.raises(QueryTooLargeError):
        check_sheet_limits(test_list)

def test_multiple_batches():
    large_data = [[random.randint(1,1000) for _ in range(1000)] for _ in range(1000)]
    batches = batch_values(large_data)
    reconstructed_data = []
    for batch in batches:
        reconstructed_data.extend(batch)
    assert large_data == reconstructed_data
    assert len(batches) > 1

def test_single_batch():
    small_data = [['a', 'b', 'c'], [0, 0, 0]]
    batches = batch_values(small_data)
    assert len(batches) == 1
    assert small_data == batches[0]
