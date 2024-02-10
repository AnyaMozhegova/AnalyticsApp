import pytest
from pydantic import ValidationError

from schemas.report_column import ReportColumnCreate, ReportColumnUpdate, validate_name


@pytest.mark.parametrize("name", ["Name Column 1", "a" * 10])
def test_validate_name_success(name):
    assert validate_name(name) == name


@pytest.mark.parametrize("name", ["", "a" * 21, " " * 5, " "])
def test_validate_name_failure(name):
    with pytest.raises(ValueError):
        validate_name(name)


def test_report_column_create_success():
    report_column_data = {
        "name": "Column 1",
        "column_data": [1.0, None, 2.5, 2.9],
        "indicator_values": [1, 2]
    }
    report_column = ReportColumnCreate(**report_column_data)
    assert report_column.name == report_column_data["name"]
    assert report_column.column_data == report_column_data["column_data"]
    assert report_column.indicator_values == report_column_data["indicator_values"]


def test_report_column_create_success_no_indicator_values():
    report_column_data = {
        "name": "Column 1",
        "column_data": [1.0, None, 2.5, 2.9],
    }
    report_column = ReportColumnCreate(**report_column_data)
    assert report_column.name == report_column_data["name"]
    assert report_column.column_data == report_column_data["column_data"]
    assert report_column.indicator_values is None


def test_report_column_create_failure():
    report_column_data = {
        "name": " " * 5,
        "column_data": [1.0, None, 2.5, 2.9],
    }
    with pytest.raises(ValidationError):
        ReportColumnCreate(**report_column_data)


def test_report_column_update_success():
    report_column_data = {
        "indicator_values": [1, 2]
    }
    report_column = ReportColumnUpdate(**report_column_data)
    assert report_column.indicator_values == report_column_data["indicator_values"]


def test_report_column_update_failure_not_float():
    report_column_data = {
        "indicator_values": [1, 2, "a"]
    }
    with pytest.raises(ValidationError):
        ReportColumnUpdate(**report_column_data)


def test_report_column_update_failure_none():
    report_column_data = {
        "indicator_values": None
    }
    with pytest.raises(ValidationError):
        ReportColumnUpdate(**report_column_data)
