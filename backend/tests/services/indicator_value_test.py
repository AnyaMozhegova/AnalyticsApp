from datetime import datetime
from typing import List
import pytest

from errors.bad_request import BadRequestError
from errors.not_found import NotFoundError
from errors.forbidden import ForbiddenError

from models.indicator_value import IndicatorValue
from models.report import Report
from models.report_column import ReportColumn
from models.report_indicator import ReportIndicator
from models.role import Role
from models.user import User

from schemas.indicator_value import IndicatorValueCreate, IndicatorValuesGet, IndicatorValueGetByName, IndicatorValueGet
from services.indicator_value import create_indicator_value, delete_indicator_value, get_indicator_values, \
    get_indicator_value, get_indicator_value_by_name

from services.indicator_value import get_indicator_values
from services.utils import filter_column_data

from tests.conftest import clean_up_test, connect_test

REPORT_INDICATORS = ["Median", "Mean", "Mode", "Quartile q1", "Quartile q2", "Quartile q3", "Outliers number",
                     "Variation range"]


def create_user() -> User:
    customer_role = Role(name='customer').save()
    user = User(name='customer_user', email="customer@gmail.com", password="customer_password",
                role=customer_role)
    user.save()
    return user


def create_columns() -> List[ReportColumn]:
    column_1 = ReportColumn(name="Column 1", column_data=[2.0, 1.0, 3.0, 6.0, None, None, 1.0],
                            indicator_values=[])
    column_1.save()
    column_2 = ReportColumn(name="Column 2", column_data=[1.5, None, 4.5, 3, None, 7.2, 0.8],
                            indicator_values=[])
    column_2.save()
    return [column_1, column_2]


def create_report(user: User, columns: List[ReportColumn]) -> Report:
    report = Report(user=user, report_link="test_link", date_uploaded=datetime.strptime("01.01.2024", "%d.%m.%Y"),
                    columns=columns,
                    fits_discriminant_analysis=False, fits_correlation_analysis=False)
    report.save()
    return report


def create_report_indicators(column):
    indicator_value_create: IndicatorValueCreate = None
    for report_indicator_name in REPORT_INDICATORS:
        report_indicator = ReportIndicator(name=report_indicator_name).save()
        if report_indicator_name == "Median":
            indicator_value_create = IndicatorValueCreate(column=column.id, report_indicator=report_indicator.id)
    return indicator_value_create


@pytest.fixture(scope="function")
def db_setup():
    db_name = "test_db"
    connect_test(db_name)
    user = create_user()
    columns = create_columns()
    report = create_report(user, columns)
    indicator_value_create = create_report_indicators(columns[0])
    yield indicator_value_create, user, report
    clean_up_test(db_name)


def test_create_indicator_value_valid(db_setup):
    indicator_value_create, _, _ = db_setup
    indicator_value_id = create_indicator_value(indicator_value_create)
    assert indicator_value_id is not None
    created_indicator_value = IndicatorValue.objects(id=indicator_value_id).first()
    assert created_indicator_value is not None


def test_create_indicator_value_nonexistent_column(db_setup):
    indicator_value_create, _, _ = db_setup
    indicator_value_create.column = indicator_value_create.column + 100

    with pytest.raises(NotFoundError):
        create_indicator_value(indicator_value_create)


def test_create_indicator_value_nonexistent_report_indicator(db_setup):
    indicator_value_create, _, _ = db_setup
    indicator_value_create.report_indicator = indicator_value_create.report_indicator + 100

    with pytest.raises(NotFoundError):
        create_indicator_value(indicator_value_create)


def test_create_indicator_value_unregistered_calculation_method(db_setup):
    indicator_value_create, _, _ = db_setup
    report_indicator = ReportIndicator.objects(id=indicator_value_create.report_indicator).first()
    report_indicator.name = "unregistered"
    report_indicator.save()

    with pytest.raises(BadRequestError):
        create_indicator_value(indicator_value_create)


@pytest.mark.parametrize("method_name,expected_value", [
    ("Median", 2.0),
    ("Mean", 2.6),
    ("Mode", 1.0),
    ("Quartile q1", 1.0),
    ("Quartile q2", 2),
    ("Quartile q3", 3.0),
    ("Outliers number", 1),
    ("Variation range", 5),
])
def test_create_indicator_value_calculation_methods(db_setup, method_name, expected_value):
    indicator_value_create, _, _ = db_setup
    report_indicator = ReportIndicator.objects(name=method_name).first()
    new_indicator_value_create = IndicatorValueCreate(column=indicator_value_create.column,
                                                      report_indicator=report_indicator.id)

    indicator_value_id = create_indicator_value(new_indicator_value_create)
    created_indicator_value = IndicatorValue.objects(id=indicator_value_id).first()

    assert created_indicator_value.value == expected_value, \
        f"Expected {method_name} calculation to be {expected_value}, not {created_indicator_value.value}"


@pytest.mark.parametrize("method_name,expected_value", [
    ("Median", 2.0),
    ("Mean", 2.6),
    ("Mode", 1.0),
    ("Quartile q1", 1.0),
    ("Quartile q2", 2),
    ("Quartile q3", 3.0),
    ("Outliers number", 1),
    ("Variation range", 5),
])
def test_create_indicator_value_calculation_methods_without_none(db_setup, method_name, expected_value):
    indicator_value_create, _, _ = db_setup
    report_indicator = ReportIndicator.objects(name=method_name).first()
    column = ReportColumn.objects(id=indicator_value_create.column).first()
    column.column_data = filter_column_data(column)
    column.save()
    new_indicator_value_create = IndicatorValueCreate(column=indicator_value_create.column,
                                                      report_indicator=report_indicator.id)

    indicator_value_id = create_indicator_value(new_indicator_value_create)
    created_indicator_value = IndicatorValue.objects(id=indicator_value_id).first()

    assert created_indicator_value.value == expected_value, \
        f"Expected {method_name} calculation to be {expected_value}, not {created_indicator_value.value}"


def test_get_indicator_values_success(db_setup):
    indicator_value_create, user, report = db_setup
    report_indicator = ReportIndicator.objects(name="Median").first()
    new_indicator_value_create = IndicatorValueCreate(column=report.columns[0].id,
                                                      report_indicator=report_indicator.id)
    indicator_value_id = create_indicator_value(new_indicator_value_create)
    indicator_value = IndicatorValue.objects(id=indicator_value_id).first().value
    indicator_values_get = IndicatorValuesGet(user=user.id, report=report.id, column=indicator_value_create.column)
    indicator_values = get_indicator_values(indicator_values_get)
    assert indicator_values is not None
    assert len(indicator_values) == 1
    assert indicator_values[0][0] == indicator_value
    assert indicator_values[0][1] == report_indicator.name


def test_get_indicator_value_by_id_success(db_setup):
    indicator_value_create, user, report = db_setup
    report_indicator = ReportIndicator.objects(name="Median").first()
    new_indicator_value_create = IndicatorValueCreate(column=report.columns[0].id,
                                                      report_indicator=report_indicator.id)
    indicator_value_id = create_indicator_value(new_indicator_value_create)
    indicator_value_get = IndicatorValueGet(user=user.id, report=report.id, column=indicator_value_create.column,
                                            indicator_value=indicator_value_id)
    indicator_value = get_indicator_value(indicator_value_get)
    assert indicator_value is not None
    assert indicator_value.id == indicator_value_id


def test_get_indicator_value_by_id_deleted(db_setup):
    indicator_value_create, user, report = db_setup
    report_indicator = ReportIndicator.objects(name="Median").first()
    deleted_indicator_value_create = IndicatorValueCreate(column=report.columns[0].id,
                                                          report_indicator=report_indicator.id)
    indicator_value_id = create_indicator_value(deleted_indicator_value_create)
    delete_indicator_value(indicator_value_id)
    indicator_value_get = IndicatorValueGet(user=user.id, report=report.id, column=indicator_value_create.column,
                                            indicator_value=indicator_value_id)
    with pytest.raises(NotFoundError):
        get_indicator_value(indicator_value_get)


def test_get_indicator_value_by_id_not_found(db_setup):
    indicator_value_create, user, report = db_setup
    indicator_value_get = IndicatorValueGet(user=user.id, report=report.id, column=indicator_value_create.column,
                                            indicator_value=1000)
    with pytest.raises(NotFoundError):
        get_indicator_value(indicator_value_get)


def test_get_indicator_value_by_name_success(db_setup):
    indicator_value_create, user, report = db_setup
    report_indicator = ReportIndicator.objects(name="Median").first()
    new_indicator_value_create = IndicatorValueCreate(column=report.columns[0].id,
                                                      report_indicator=report_indicator.id)
    indicator_value_id = create_indicator_value(new_indicator_value_create)
    indicator_value_get_name = IndicatorValueGetByName(user=user.id, report=report.id,
                                                       column=indicator_value_create.column,
                                                       report_indicator_name="Median")
    indicator_value = get_indicator_value_by_name(indicator_value_get_name)
    assert indicator_value is not None
    assert indicator_value.id == indicator_value_id


def test_get_indicator_value_by_name_deleted(db_setup):
    indicator_value_create, user, report = db_setup
    report_indicator = ReportIndicator.objects(name="Median").first()
    deleted_indicator_value_create = IndicatorValueCreate(column=report.columns[0].id,
                                                          report_indicator=report_indicator.id)
    indicator_value_id = create_indicator_value(deleted_indicator_value_create)
    delete_indicator_value(indicator_value_id)
    indicator_value_get_name = IndicatorValueGetByName(user=user.id, report=report.id,
                                                       column=indicator_value_create.column,
                                                       report_indicator_name="Median")
    with pytest.raises(NotFoundError):
        get_indicator_value_by_name(indicator_value_get_name)


def test_get_indicator_value_by_name_not_found(db_setup):
    non_existent_name = "Nonexistent Name"
    indicator_value_create, user, report = db_setup
    indicator_value_get_name = IndicatorValueGetByName(user=user.id, report=report.id,
                                                       column=indicator_value_create.column,
                                                       report_indicator_name=non_existent_name)
    with pytest.raises(NotFoundError):
        get_indicator_value_by_name(indicator_value_get_name)


def test_get_indicator_values_column_in_different_report(db_setup):
    _, user, report = db_setup
    column_3 = ReportColumn(name="Column 3", column_data=[2.0, 1.0, 3.0, 6.0, None, None, 1.0],
                            indicator_values=[]).save()
    report_2 = Report(user=user, report_link="test_link", date_uploaded=datetime.strptime("02.02.2024", "%d.%m.%Y"),
                      columns=[column_3],
                      fits_discriminant_analysis=False, fits_correlation_analysis=False)
    report_2.save()
    different_report_column = column_3
    indicator_values_get = IndicatorValuesGet(user=user.id, report=report.id,
                                              column=different_report_column.id)
    with pytest.raises(NotFoundError):
        get_indicator_values(indicator_values_get)


def test_get_indicator_values_report_does_not_belong_to_user(db_setup):
    indicator_value_create, _, report = db_setup
    customer_role = Role.objects(name='customer').first()
    another_user = User(name='customer_user_1', email="customer_1@gmail.com", password="customer_password",
                        role=customer_role).save()
    indicator_values_get = IndicatorValuesGet(user=another_user.id, report=report.id,
                                              column=indicator_value_create.column)
    with pytest.raises(ForbiddenError):
        get_indicator_values(indicator_values_get)


def test_get_indicator_values_non_exist_user(db_setup):
    indicator_value_create, _, report = db_setup
    indicator_values_get = IndicatorValuesGet(user=100, report=report.id,
                                              column=indicator_value_create.column)
    with pytest.raises(NotFoundError):
        get_indicator_values(indicator_values_get)


def test_get_indicator_values_non_exist_report(db_setup):
    indicator_value_create, user, _ = db_setup
    indicator_values_get = IndicatorValuesGet(user=user.id, report=100,
                                              column=indicator_value_create.column)
    with pytest.raises(NotFoundError):
        get_indicator_values(indicator_values_get)
