import pytest
from pydantic import ValidationError

from schemas.report_indicator import ReportIndicatorCreate, ReportIndicatorUpdate, validate_name


@pytest.mark.parametrize("name", ["Median", "Some value", "a" * 10])
def test_validate_name_success(name):
    assert validate_name(name) == name


@pytest.mark.parametrize("name", ["", "a" * 21, " " * 5])
def test_validate_name_failure(name):
    with pytest.raises(ValueError):
        validate_name(name)


def test_report_indicator_create_success():
    report_indicator_data = {
        "name": "Median",
    }
    role = ReportIndicatorCreate(**report_indicator_data)
    assert role.name == report_indicator_data["name"]


def test_report_indicator_create_password_mismatch():
    report_indicator_data = {
        "name": " " * 5
    }
    with pytest.raises(ValidationError):
        ReportIndicatorCreate(**report_indicator_data)


@pytest.fixture
def created_indicator():
    return ReportIndicatorCreate(name="Initial Name")


def test_report_indicator_update_success(created_indicator):
    updated_data = {"name": "Updated Valid Name"}
    updated_indicator = ReportIndicatorUpdate(**updated_data)

    assert updated_indicator.name == updated_data["name"], "The name should have been updated successfully."


@pytest.mark.parametrize("invalid_name", ["", " " * 21, "\t\n"])
def test_report_indicator_update_failure(created_indicator, invalid_name):
    updated_data = {"name": invalid_name}
    with pytest.raises(ValidationError):
        ReportIndicatorUpdate(**updated_data)
