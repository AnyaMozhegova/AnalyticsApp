import logging

import numpy as np
from scipy import stats
from typing import Callable, Dict, List, Optional

from errors.not_found import NotFoundError
from errors.bad_request import BadRequestError
from errors.forbidden import ForbiddenError

from models.report_indicator import ReportIndicator
from models.report import Report
from models.user import User
from models.report_column import ReportColumn
from models.indicator_value import IndicatorValue

from schemas.indicator_value import IndicatorValueCreate, IndicatorValueGet, IndicatorValueGetBase, \
    IndicatorValueGetByName, \
    IndicatorValuesGet

from services.utils import filter_column_data

calculation_methods: Dict[str, Callable[[List[float]], float]] = {}

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s:  %(asctime)s  %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


def register_calculation(name: str):
    def decorator(func: Callable[[List[float]], float]):
        calculation_methods[name] = func
        return func

    return decorator


@register_calculation('median')
def calculate_median(column_data: List[float]) -> float:
    data = np.array(column_data, dtype=float)
    return float(np.median(data))


@register_calculation('mean')
def calculate_mean(column_data: List[float]) -> float:
    data = np.array(column_data, dtype=float)
    return float(np.mean(data))


@register_calculation('mode')
def calculate_mode(column_data: List[float]) -> float:
    data = np.array(column_data, dtype=float)
    logging.info(data)
    return float(stats.mode(data).mode)  # type: ignore


@register_calculation('quartile q1')
def calculate_quartile_q1(column_data: List[float]) -> float:
    return np.quantile(column_data, .25)


@register_calculation('quartile q2')
def calculate_quartile_q2(column_data: List[float]) -> float:
    return np.quantile(column_data, .5)


@register_calculation('quartile q3')
def calculate_quartile_q3(column_data: List[float]) -> float:
    return np.quantile(column_data, .75)


@register_calculation('outliers number')
def calculate_outliers_number(column_data: List[float]) -> float:
    q1 = np.quantile(column_data, .25)
    q3 = np.quantile(column_data, .75)
    iqr = q3 - q1
    min_range = q1 - iqr
    max_range = q3 + iqr
    return len([x for x in column_data if x < min_range or x > max_range])


@register_calculation('variation range')
def calculate_variation_range(column_data: List[float]) -> float:
    return max(column_data) - min(column_data)


def create_indicator_value(indicator_value_create: IndicatorValueCreate) -> int:
    if not (column := ReportColumn.objects(id=indicator_value_create.column, is_active=True).first()):
        raise NotFoundError(
            f"Could not create indicator value. There is no column with id = {indicator_value_create.column}")

    if not (report_indicator := ReportIndicator.objects(id=indicator_value_create.report_indicator).first()):
        raise NotFoundError(
            f"Could not create indicator value. There is no report indicator with "
            f"id = {indicator_value_create.report_indicator}")

    if not (calculation_method := calculation_methods.get(report_indicator.name.lower())):
        raise BadRequestError(f"No calculation method registered for {report_indicator.name}")
    if filtered_column_data := filter_column_data(column):
        calculated_value = calculation_method(filtered_column_data)
        indicator_value = IndicatorValue(report_indicator=report_indicator, value=calculated_value, is_active=True)
    else:
        indicator_value = IndicatorValue(report_indicator=report_indicator, value=None, is_active=True)
    indicator_value.save()
    column.indicator_values.append(indicator_value)
    column.save()
    return indicator_value.id


def delete_indicator_value(indicator_value_id: int):
    if not (indicator_value := IndicatorValue.objects(id=indicator_value_id, is_active=True).first()):
        raise NotFoundError(f"Could not delete indicator value. There is no such entity with id = {indicator_value_id}")
    indicator_value.is_active = False
    indicator_value.save()


def validate_indicator_value_column(get_base: IndicatorValueGetBase) -> Optional[ReportColumn]:
    if not (user := User.objects(id=get_base.user, is_active=True).first()):
        raise NotFoundError(
            f"Could not get indicator values. There is no user with id = {get_base.user}")
    if not (report := Report.objects(id=get_base.report, is_active=True).first()):
        raise NotFoundError(
            f"Could not get indicator values. There is no report with id = {get_base.report}")
    if report.user.id != user.id:
        raise ForbiddenError(f"Could not get indicator values. Report with id = {get_base.report} "
                             f"does not belongs to user with id = {user.id}")
    if not (column := ReportColumn.objects(id=get_base.column, is_active=True).first()):
        raise NotFoundError(
            f"Could not get indicator values. There is no column with id = {get_base.column}")
    if column not in report.columns:
        raise NotFoundError(f"Could not get indicator values. There is no column with id = {get_base.column} "
                            f"in report with id = {get_base.report}")
    return column


def validate_indicator_value_id(column: ReportColumn, indicator_value_id: int):
    if not (indicator_value := IndicatorValue.objects(id=indicator_value_id, is_active=True).first()):
        raise NotFoundError(f"Could not get indicator value. There is no such entity with id = {indicator_value_id}")
    if indicator_value not in column.indicator_values:
        raise NotFoundError(f"Could not get indicator value. There is no such entity in column with id = {column.id}")
    return indicator_value


def validate_indicator_value_name(column: ReportColumn, report_indicator_name: str):
    if not (report_indicator := ReportIndicator.objects(name=report_indicator_name).first()):
        raise NotFoundError(
            f"Could not get indicator value. There is no report indicator with name = {report_indicator_name}")
    indicator_values = column.indicator_values
    for indicator_value in indicator_values:
        if indicator_value.report_indicator.id == report_indicator.id and indicator_value.is_active:
            return indicator_value
    raise NotFoundError(
        f"Could not get indicator value. There is no such entity with report indicator = {report_indicator_name} "
        f"in column with id = {column.id}")


def get_indicator_values(indicator_values_get: IndicatorValuesGet) -> [[float, str]]:
    column = validate_indicator_value_column(indicator_values_get)
    return [[indicator_value.value, indicator_value.report_indicator.name] for indicator_value in
            column.indicator_values if indicator_value.is_active]


def get_indicator_value(indicator_value_get: IndicatorValueGet) -> Optional[IndicatorValue]:
    column = validate_indicator_value_column(indicator_value_get)
    return validate_indicator_value_id(column, indicator_value_get.indicator_value)


def get_indicator_value_by_name(indicator_value_get_name: IndicatorValueGetByName) -> Optional[IndicatorValue]:
    column = validate_indicator_value_column(indicator_value_get_name)
    return validate_indicator_value_name(column, indicator_value_get_name.report_indicator_name)
