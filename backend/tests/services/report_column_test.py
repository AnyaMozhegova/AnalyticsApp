from typing import List

import pytest

from models.report_column import ReportColumn
from models.report_indicator import ReportIndicator
from schemas.indicator_value import IndicatorValueCreate
from schemas.report_column import ReportColumnCreate
from services.indicator_value import create_indicator_value
from services.report_column import create_report_column, get_report_column, get_report_column_by_name, \
    get_report_columns, delete_report_column
from tests.conftest import clean_up_test, connect_test

from errors.not_found import NotFoundError

from models.indicator_value import IndicatorValue


def create_columns() -> List[ReportColumn]:
    column_1 = ReportColumn(name="Column 1", column_data=[2.0, 1.0, 3.0, 6.0, None, None, 1.0],
                            indicator_values=[], is_active=True)
    column_1.save()
    column_2 = ReportColumn(name="Column 2", column_data=[1.5, None, 4.5, 3, None, 7.2, 0.8],
                            indicator_values=[], is_active=True)
    column_2.save()
    return [column_1, column_2]


def create_indicator_values(column_1: ReportColumn, column_2: ReportColumn):
    report_indicator = ReportIndicator(name="Median").save()
    indicator_value_1 = create_indicator_value(
        IndicatorValueCreate(column=column_1.id, report_indicator=report_indicator.id))
    indicator_value_2 = create_indicator_value(
        IndicatorValueCreate(column=column_2.id, report_indicator=report_indicator.id))
    return indicator_value_1, indicator_value_2


@pytest.fixture(scope="function")
def db_setup():
    db_name = "test_db"
    connect_test(db_name)
    columns = create_columns()
    indicator_values = create_indicator_values(columns[0], columns[1])
    yield columns, indicator_values
    clean_up_test(db_name)


def test_create_report_column(db_setup):
    report_column_create = ReportColumnCreate(name="New Column", column_data=[5.0, 6.0], indicator_values=[])
    report_column_id = create_report_column(report_column_create)
    assert ReportColumn.objects(id=report_column_id).first() is not None


def test_get_report_columns(db_setup):
    columns, _ = db_setup
    result = get_report_columns()
    assert len(result) == 2
    assert list(map(lambda column: column.id, columns)) == list(map(lambda column: column.id, result))


def test_get_report_columns_with_inactive(db_setup):
    columns, _ = db_setup
    columns[0].is_active = False
    columns[0].save()
    result = get_report_columns()
    assert len(result) == 1
    assert columns[1].id == result[0].id


def test_get_report_column(db_setup):
    columns, _ = db_setup
    result = get_report_column(columns[0].id)
    assert result is not None
    assert result.name == columns[0].name


def test_get_report_column_inactive(db_setup):
    columns, _ = db_setup
    columns[0].is_active = False
    columns[0].save()
    with pytest.raises(NotFoundError):
        get_report_column(columns[0].id)


def test_get_report_column_not_found(db_setup):
    columns, _ = db_setup
    with pytest.raises(NotFoundError):
        get_report_column(columns[0].id + 1000)


def test_get_report_column_by_name(db_setup):
    columns, _ = db_setup
    result = get_report_column_by_name(columns[0].name)
    assert result is not None
    assert result.id == columns[0].id


def test_get_report_column_by_name_inactive(db_setup):
    columns, _ = db_setup
    columns[0].is_active = False
    columns[0].save()
    with pytest.raises(NotFoundError):
        get_report_column_by_name(columns[0].name)


def test_get_report_column_by_name_not_found(db_setup):
    with pytest.raises(NotFoundError):
        get_report_column_by_name("Not Existed Column")


def test_delete_report_column(db_setup):
    columns, _ = db_setup
    delete_report_column(columns[0].id)
    deleted_column = ReportColumn.objects(id=columns[0].id).first()
    assert deleted_column is not None
    assert deleted_column.is_active is False
    deleted_indicator_values = IndicatorValue.objects(id__in=columns[0].indicator_values)
    for deleted_indicator_value in deleted_indicator_values:
        assert deleted_indicator_value is not None
        assert deleted_indicator_value.is_active is False


def test_delete_report_column_inactive(db_setup):
    columns, _ = db_setup
    columns[0].is_active = False
    columns[0].save()
    with pytest.raises(NotFoundError):
        delete_report_column(columns[0].id)
        not_deleted_column = ReportColumn.objects(id=columns[0].id).first()
        assert not_deleted_column is not None
        assert not_deleted_column.is_active is False
        not_deleted_indicator_values = IndicatorValue.objects(id__in=columns[0].indicator_values)
        for deleted_indicator_value in not_deleted_indicator_values:
            assert deleted_indicator_value is not None
            assert deleted_indicator_value.is_active is True


def test_delete_report_column_not_found(db_setup):
    columns, _ = db_setup
    with pytest.raises(NotFoundError):
        delete_report_column(columns[0].id + 1000)
