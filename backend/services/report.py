import os
import shutil
from datetime import datetime
from typing import List, Optional

import numpy as np
import pandas as pd
from errors.bad_request import BadRequestError
from errors.not_found import NotFoundError
from fastapi import Depends, UploadFile
from models.report import Report
from models.report_column import ReportColumn
from models.user import User
from schemas.indicator_value import IndicatorValueCreate
from services.indicator_value import create_indicator_value
from services.report_indicator import get_report_indicators

from models.customer import Customer
from services.user import get_current_user

from services.report_column import delete_report_column


def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)


def check_report_extension(input_file: UploadFile):
    allowed_extensions = ["xls", "xlsx"]
    if input_file.filename.split(".")[-1] not in allowed_extensions:
        raise BadRequestError("File extension not allowed")


def check_column_names(df) -> bool:
    if df.columns.duplicated().any() or df.columns.isnull().any() or any(column.strip() == "" for column in df.columns):
        raise BadRequestError("All columns must have unique, non-empty names")
    return True


def save_column(column_data_name: str, column_data_floats: List[Optional[float]], saved_columns: List[ReportColumn]):
    report_column = ReportColumn(name=column_data_name, column_data=column_data_floats)
    report_column.save()
    saved_columns.append(report_column)


def validate_column_content(df, column, saved_columns: List[ReportColumn]):
    column_data_content = df[column].tolist()[1:]
    column_data = [None if pd.isnull(x) else x for x in column_data_content]

    column_data_floats: List[Optional[float]] = []
    valid_column = True
    for item in column_data:
        if item is None or item == '':
            column_data_floats.append(None)
            continue
        try:
            column_data_floats.append(float(item))
        except ValueError:
            valid_column = False
            break
    if not valid_column:
        raise BadRequestError("Could not save file. Dataset contains non numeric data")
    present_floats = [value for value in column_data_floats if value]
    if valid_column and any(isinstance(x, float) for x in column_data_floats) and len(present_floats) >= 3:
        save_column(column, column_data_floats, saved_columns)


def validate_report_file(file_path: str) -> List[ReportColumn]:
    saved_columns: List[ReportColumn] = []
    df = pd.read_excel(file_path, engine='openpyxl', dtype=str)
    try:
        check_column_names(df)
    except BadRequestError as e:
        delete_file(file_path)
        raise BadRequestError(e)
    for column in df.columns:
        validate_column_content(df, column, saved_columns)
    if len(saved_columns) == 0:
        delete_file(file_path)
        raise BadRequestError("Could not save file. There is no valid columns in the dataset")
    return saved_columns


def calculate_indicator_values(saved_columns: List[ReportColumn]):
    report_indicators = get_report_indicators()
    for report_indicator in report_indicators:
        for column in saved_columns:
            indicator_value_create = IndicatorValueCreate(report_indicator=report_indicator.id,
                                                          column=column.id)
            create_indicator_value(indicator_value_create)


def check_fits_discriminant_analysis(report_columns: List[ReportColumn]) -> bool:
    from scipy.stats import kstest
    df = columns_to_df(report_columns)
    for column in df.columns:
        values = df[column].values
        _, p = kstest(values, 'norm')
        if p <= 0.05:
            return False
    return True


def columns_to_df(columns: List[ReportColumn]) -> pd.DataFrame:
    active_columns = [col for col in columns if col.is_active]
    data_dict = {col.name: col.column_data for col in active_columns}

    return pd.DataFrame(data_dict)


def calculate_strengthened_weakened_relationships(df: pd.DataFrame) -> (int, int):
    strengthened, weakened = 0, 0

    for i in range(len(df.columns)):
        for j in range(i + 1, len(df.columns)):
            data = df[[df.columns[i], df.columns[j]]]
            corr_pair = np.abs(data.corr().iloc[0, 1])
            corr_partial = np.abs(data.corr(method='spearman').iloc[0, 1])
            if corr_pair > corr_partial:
                strengthened += 1
            else:
                weakened += 1

    return strengthened, weakened


def check_fits_correlation_analysis(report_columns: List[ReportColumn]) -> bool:
    df = columns_to_df(report_columns)
    strengthened, weakened = calculate_strengthened_weakened_relationships(df)

    return strengthened > weakened


async def create_report(report_file: UploadFile, current_user: User = Depends(get_current_user)) -> int:
    if not current_user or not (customer := Customer.objects(id=current_user.id, is_active=True).first()):
        raise NotFoundError(f"Could not upload report. There is no customer {current_user}")
    file_path = await upload_report(customer, report_file)
    saved_columns = validate_report_file(file_path)
    calculate_indicator_values(saved_columns)
    fits_discriminant_analysis = check_fits_discriminant_analysis(saved_columns)
    fits_correlation_analysis = check_fits_correlation_analysis(saved_columns)
    report = Report(user=current_user, report_link=file_path, date_uploaded=datetime.now(), columns=saved_columns,
                    fits_discriminant_analysis=fits_discriminant_analysis,
                    fits_correlation_analysis=fits_correlation_analysis).save()
    return report.id


def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    file_path = os.path.join(destination, upload_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    upload_file.file.close()
    return file_path


async def upload_report(customer: Customer, report_file: UploadFile):
    check_report_extension(report_file)
    destination = f'{os.getcwd()}/user_data/{customer.id}/report_files/'
    does_exists = os.path.exists(destination)
    if not does_exists:
        os.makedirs(destination)
    file_path = save_upload_file(report_file, destination)
    return file_path


def get_current_customer_reports(current_user: User = Depends(get_current_user)) -> List[Report]:
    if not current_user or not (customer := Customer.objects(id=current_user.id, is_active=True).first()):
        raise NotFoundError(f"Could not get customer reports for {current_user}. Customer does not exist.")
    return Report.objects(is_active=True, user=customer).order_by('-date_uploaded')


def get_customer_reports(customer_id: int) -> List[Report]:
    if not (customer := Customer.objects(id=customer_id, is_active=True).first()):
        raise NotFoundError(f"Could not get customer reports with id = {customer_id}. Customer does not exist.")
    return Report.objects(is_active=True, user=customer).order_by('-date_uploaded')


def get_current_customer_report(report_id: int, current_user: User = Depends(get_current_user)) -> Optional[Report]:
    if not current_user or not (customer := Customer.objects(id=current_user.id, is_active=True).first()):
        raise NotFoundError(
            f"Could not get customer report with id {report_id} for {current_user}. Customer does not exist.")
    if not (report := Report.objects(id=report_id, is_active=True, user=customer).first()):
        raise NotFoundError(f"Could not get customer report with id {report_id}. Report does not exist.")
    return report


def get_customer_report(report_id: int, customer_id: int) -> Optional[Report]:
    if not (customer := Customer.objects(id=customer_id, is_active=True).first()):
        raise NotFoundError(
            f"Could not get customer report with id {report_id} for customer {customer_id}. Customer does not exist.")
    if not (report := Report.objects(id=report_id, is_active=True, user=customer).first()):
        raise NotFoundError(f"Could not get report with id {report_id}. Report does not exist.")
    return report


def delete_report(report_id: int, current_user: User = Depends(get_current_user)) -> None:
    if not current_user or not (customer := Customer.objects(id=current_user.id, is_active=True).first()):
        raise NotFoundError(f"Could not delete customer {current_user}. Customer does not exist.")
    if not (report := Report.objects(id=report_id, is_active=True, user=customer).first()):
        raise NotFoundError(f"Could not delete report with id {report_id}. Report does not exist.")
    report.is_active = False
    report.save()
    for report_column in report.columns:
        delete_report_column(report_column.id)


def get_report_file(report_id: int, current_user: User = Depends(get_current_user)) -> str:
    if not current_user or not (customer := Customer.objects(id=current_user.id, is_active=True).first()):
        raise NotFoundError(f"Could not get report file with id = {report_id}. Customer does not exist.")
    if not (report := Report.objects(id=report_id, is_active=True, user=customer).first()):
        raise NotFoundError(f"Could not get report file with id {report_id}. Report does not exist.")
    file_path = report.report_link
    if not os.path.exists(file_path):
        raise NotFoundError(f"Could not get report file with id {report_id}. File does not exist.")
    return report.report_link
