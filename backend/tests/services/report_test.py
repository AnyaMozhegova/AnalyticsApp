import os
import shutil
from datetime import datetime
from io import BytesIO
from typing import List

import numpy as np
import pandas as pd
import pytest
from errors.bad_request import BadRequestError
from errors.not_found import NotFoundError
from fastapi import UploadFile
from mock import patch
from models.report_column import ReportColumn
from services.report import calculate_strengthened_weakened_relationships, check_fits_correlation_analysis, \
    columns_to_df, check_column_names, check_report_extension, upload_report, validate_column_content, \
    validate_report_file, check_fits_discriminant_analysis, create_report, get_current_customer_reports, \
    get_customer_reports, get_current_customer_report, get_customer_report, delete_report

from tests.conftest import clean_up_test, connect_test, create_customer_user

from models.customer import Customer
from models.report import Report

VALID_NAME = "valid.xlsx"
INVALID_NAME = "invalid.xlsx"
DB_NAME = "test_db"


def create_upload_file(filename: str, data: pd.DataFrame) -> UploadFile:
    file_path = f'tests/{filename}'
    data.to_excel(file_path, index=False)
    return UploadFile(filename=filename, file=open(file_path, 'rb'))


def cleanup_files():
    shutil.rmtree('user_data', ignore_errors=True)
    for file in os.listdir('tests'):
        if file.endswith(".xls") or file.endswith(".xlsx"):
            os.remove(os.path.join('tests', file))


def create_test_report(customer: Customer, is_active: bool = True):
    columns = [ReportColumn(name="Column 1", column_data=[2.0, 1.0, 3.0, 6.0, None, None, 1.0],
                            indicator_values=[]).save()]
    return Report(user=customer, report_link="link", date_uploaded=datetime.strptime("01.01.2024", "%d.%m.%Y"),
                  columns=columns, fits_discriminant_analysis=False,
                  fits_correlation_analysis=False,
                  is_active=is_active).save()


@pytest.fixture(scope="function")
def db_setup():
    connect_test(DB_NAME)
    user = create_customer_user()
    yield user
    clean_up_test(DB_NAME)
    cleanup_files()


GET_CURRENT_USER_PATH = 'services.user.get_current_user'


def test_check_report_extension_valid(db_setup):
    file = create_upload_file(VALID_NAME, pd.DataFrame())
    try:
        check_report_extension(file)
    finally:
        file.file.close()


def test_check_report_extension_invalid(db_setup):
    file = UploadFile(filename="invalid.txt", file=BytesIO(b''))
    with pytest.raises(BadRequestError):
        try:
            check_report_extension(file)
        finally:
            file.file.close()


def test_check_column_names_valid(db_setup):
    df = pd.DataFrame(columns=["column a", "column b"])
    check_column_names(df)


def test_check_column_names_duplicate(db_setup):
    df = pd.DataFrame(columns=["test", "test"])
    with pytest.raises(BadRequestError):
        check_column_names(df)


def test_check_column_names_missing(db_setup):
    df = pd.DataFrame(columns=["", "valid"])
    with pytest.raises(BadRequestError):
        check_column_names(df)


def test_validate_column_content_with_strings(db_setup):
    data = pd.DataFrame({
        'A': ['Header', '1', 'two', '3.0', '4.0'],  # 'two' is not a valid float
    })
    file = create_upload_file(INVALID_NAME, data)
    saved_columns = []
    with pytest.raises(BadRequestError):
        validate_column_content(data, 'A', saved_columns)
        assert len(saved_columns) == 0, "No columns should be saved for invalid content"
    file.file.close()


def test_validate_column_content_with_none(db_setup):
    data = pd.DataFrame({
        'A': [1, None, 3.0, 2.5, 2.2, 10, 20],
    })
    file = create_upload_file(INVALID_NAME, data)
    saved_columns = []
    validate_column_content(data, 'A', saved_columns)
    assert len(saved_columns) == 1
    file.file.close()


def test_validate_column_content_with_empty_column(db_setup):
    data = pd.DataFrame({
        'A': [None, None, None, None, None]
    })
    file = create_upload_file(INVALID_NAME, data)
    saved_columns = []
    validate_column_content(data, 'A', saved_columns)
    assert len(saved_columns) == 0, "No columns should be saved for empty column"
    file.file.close()


@pytest.mark.asyncio
async def test_upload_report_valid_file(db_setup):
    user = db_setup
    data = pd.DataFrame({'A': [1, 2, 3, 4, 7, 7], 'B': [4, 5, 6, 7, 7, 7]})
    file = create_upload_file(VALID_NAME, data)
    file_path = await upload_report(user, file)
    try:
        validate_report_file(file_path)
        assert os.path.exists(file_path)
    finally:
        file.file.close()


@pytest.mark.asyncio
async def test_upload_report_with_empty_column(db_setup):
    user = db_setup
    data = pd.DataFrame(
        {'A': [1, 2, 3, 4, 5, 5], 'B': [4, 5, 6, 7, 7, 7], 'C': [np.nan, np.nan, np.nan, 3, 4, 5]})
    file = create_upload_file(VALID_NAME, data)
    file_path = await upload_report(user, file)
    try:
        validate_report_file(file_path)
        assert os.path.exists(file_path)
    finally:
        file.file.close()


@pytest.mark.asyncio
async def test_upload_report_invalid_names(db_setup):
    user = db_setup
    data = pd.DataFrame({' ': [1, 2, 3, 4], 'B': [4, 5, 6, 7]})
    file = create_upload_file(INVALID_NAME, data)
    file_path = await upload_report(user, file)
    with pytest.raises(BadRequestError):
        validate_report_file(file_path)
        assert os.path.exists(file_path) is False
    file.file.close()


def mock_report_columns() -> List[ReportColumn]:
    mock_columns = [
        ReportColumn(is_active=True, name='Column1', column_data=[1.5, 2, 3.5, 7.5, 5]),
        ReportColumn(is_active=True, name='Column2', column_data=[3.2, 2.5, 1, 4.5, 5]),
        ReportColumn(is_active=False, name='InactiveColumn', column_data=[None, None, None, None]),
        # This should be ignored
        ReportColumn(is_active=True, name='Column3', column_data=[6, 7.2, None, 2.4, 5]),
        ReportColumn(is_active=True, name='Column4', column_data=[13.2, -20.65, 1.4, 22.6, -18.73]),
        ReportColumn(is_active=True, name='Column5', column_data=[10.43, -7.54, 8.99, -5.23, 0.45])
    ]
    return mock_columns


def test_columns_to_df(db_setup):
    report_columns = mock_report_columns()
    df = columns_to_df(report_columns)
    assert 'Column1' in df.columns and 'Column2' in df.columns
    assert 'InactiveColumn' not in df.columns  # Inactive column should be ignored
    assert 'Column3' in df.columns


def test_calculate_strengthened_weakened_relationships(db_setup):
    report_columns = mock_report_columns()
    df = columns_to_df(report_columns)
    strengthened, weakened = calculate_strengthened_weakened_relationships(df)
    assert isinstance(strengthened, int) and isinstance(weakened, int)
    assert strengthened == 5
    assert weakened == 5


def test_check_fits_correlation_analysis_false(db_setup):
    report_columns = mock_report_columns()
    result = check_fits_correlation_analysis(report_columns)
    assert isinstance(result, bool)
    assert result is False


def test_check_fits_correlation_analysis_true(db_setup):
    report_columns = mock_report_columns()[:-2]
    result = check_fits_correlation_analysis(report_columns)
    assert isinstance(result, bool)
    assert result is True


def test_check_fits_discriminant_analysis_false(db_setup):
    report_columns = mock_report_columns()[:-2]
    assert check_fits_discriminant_analysis(report_columns) is False


def test_check_fits_discriminant_analysis_true(db_setup):
    report_columns = mock_report_columns()[-2:]
    assert check_fits_discriminant_analysis(report_columns) is True


@pytest.mark.asyncio
async def test_create_report_success(db_setup):
    user = db_setup
    report_columns = mock_report_columns()
    df = columns_to_df(report_columns)
    file = create_upload_file(VALID_NAME, df)
    report_id = await create_report(file, user)
    assert isinstance(report_id, int)
    assert report_id is not None


@pytest.mark.asyncio
async def test_create_report_failure(db_setup):
    report_columns = mock_report_columns()
    df = columns_to_df(report_columns)
    file = create_upload_file(VALID_NAME, df)
    with pytest.raises(NotFoundError):
        await create_report(file, None)


def test_get_current_customer_reports(db_setup):
    customer = db_setup
    report = create_test_report(customer, True)
    with patch(GET_CURRENT_USER_PATH, return_value=customer):
        result = get_current_customer_reports(customer)
        assert len(result) == 1
        assert result[0].id == report.id


def test_get_current_customer_reports_inactive(db_setup):
    customer = db_setup
    create_test_report(customer, False)
    with patch(GET_CURRENT_USER_PATH, return_value=customer):
        result = get_current_customer_reports(customer)
        assert len(result) == 0


def test_get_current_customer_reports_customer_not_found(db_setup):
    customer = db_setup
    create_test_report(customer)
    with patch(GET_CURRENT_USER_PATH, return_value=None), pytest.raises(NotFoundError):
        get_current_customer_reports(None)


def test_get_customer_reports(db_setup):
    customer = db_setup
    report = create_test_report(customer, True)
    result = get_customer_reports(customer.id)
    assert len(result) == 1
    assert result[0].id == report.id


def test_get_customer_reports_inactive(db_setup):
    customer = db_setup
    create_test_report(customer, False)
    result = get_customer_reports(customer.id)
    assert len(result) == 0


def test_get_customer_reports_customer_not_found(db_setup):
    customer = db_setup
    create_test_report(customer)
    with pytest.raises(NotFoundError):
        get_customer_reports(customer.id + 1000)


def test_get_current_customer_report(db_setup):
    customer = db_setup
    report = create_test_report(customer, True)
    with patch(GET_CURRENT_USER_PATH, return_value=customer):
        result = get_current_customer_report(report.id, customer)
        assert result is not None
        assert result.id == report.id


def test_get_current_customer_report_inactive(db_setup):
    customer = db_setup
    report = create_test_report(customer, False)
    with patch(GET_CURRENT_USER_PATH, return_value=customer), pytest.raises(NotFoundError):
        get_current_customer_report(report.id, customer)


def test_get_current_customer_report_customer_not_found(db_setup):
    customer = db_setup
    report = create_test_report(customer)
    with patch(GET_CURRENT_USER_PATH, return_value=None), pytest.raises(NotFoundError):
        get_current_customer_report(report.id, None)


def test_get_current_customer_report_not_found(db_setup):
    customer = db_setup
    report = create_test_report(customer)
    with patch(GET_CURRENT_USER_PATH, return_value=None), pytest.raises(NotFoundError):
        get_current_customer_report(report.id + 1000, customer)


def test_get_customer_report(db_setup):
    customer = db_setup
    report = create_test_report(customer, True)
    result = get_customer_report(report.id, customer.id)
    assert result is not None
    assert result.id == report.id


def test_get_customer_report_inactive(db_setup):
    customer = db_setup
    report = create_test_report(customer, False)
    with pytest.raises(NotFoundError):
        get_customer_report(report.id, customer.id)


def test_get_customer_report_customer_not_found(db_setup):
    customer = db_setup
    report = create_test_report(customer)
    with pytest.raises(NotFoundError):
        get_customer_report(report.id, customer.id + 1000)


def test_get_customer_report_not_found(db_setup):
    customer = db_setup
    report = create_test_report(customer)
    with pytest.raises(NotFoundError):
        get_customer_report(report.id + 1000, customer.id)


def test_delete_report(db_setup):
    customer = db_setup
    report = create_test_report(customer)
    delete_report(report.id, customer)
    deleted_report = Report.objects(id=report.id).first()
    assert deleted_report is not None
    assert deleted_report.is_active is False
    deleted_columns = ReportColumn.objects(id__in=list(map(lambda report_column: report_column.id, report.columns)))
    for deleted_column in deleted_columns:
        assert deleted_column is not None
        assert deleted_column.is_active is False


def test_delete_report_inactive(db_setup):
    customer = db_setup
    report = create_test_report(customer, False)
    with pytest.raises(NotFoundError):
        delete_report(report.id, customer)
        not_deleted_report = Report.objects(id=report.id).first()
        assert not_deleted_report is not None
        assert not_deleted_report.is_active is False
        not_deleted_columns = ReportColumn.objects(
            id__in=list(map(lambda report_column: report_column.id, report.columns)))
        for not_deleted_column in not_deleted_columns:
            assert not_deleted_column is not None
            assert not_deleted_column.is_active is True


def test_delete_report_not_found(db_setup):
    customer = db_setup
    report = create_test_report(customer)
    with pytest.raises(NotFoundError):
        delete_report(report.id + 1000, customer)


def test_delete_report_customer_not_found(db_setup):
    customer = db_setup
    report = create_test_report(customer)
    with pytest.raises(NotFoundError):
        delete_report(report.id, None)
