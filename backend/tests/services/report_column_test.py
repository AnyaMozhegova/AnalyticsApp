from typing import List

import pytest

from models.report_column import ReportColumn
from models.report_indicator import ReportIndicator
from schemas.indicator_value import IndicatorValueCreate
from schemas.report_column import ReportColumnCreate
from services.indicator_value import create_indicator_value
from services.report_column import create_report_column
from tests.conftest import clean_up_test, connect_test


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
