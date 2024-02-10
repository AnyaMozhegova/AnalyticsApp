from typing import List, Optional

from errors.not_found import NotFoundError
from models.report_column import ReportColumn
from schemas.report_column import ReportColumnCreate


def create_report_column(report_column_create: ReportColumnCreate) -> int:
    report_column = ReportColumn(name=report_column_create.name,
                                 column_data=report_column_create.column_data,
                                 indicator_values=report_column_create.indicator_values)
    report_column.save()
    return report_column.id


def delete_report_column(report_column_id):
    if not (report_column := ReportColumn.objects(id=report_column_id, is_active=True).first()):
        raise NotFoundError(f"Could not delete report column. There is no such entity with id = {report_column_id}")
    report_column.is_active = False
    report_column.save()


def get_report_columns() -> List[ReportColumn]:
    return ReportColumn.objects(is_active=True)


def get_report_column(report_column_id: int) -> Optional[ReportColumn]:
    if report_column := ReportColumn.objects(id=report_column_id, is_active=True).first():
        return report_column
    raise NotFoundError(
        f"Could not get report column with id = {report_column_id}. There is no such entity")


def get_report_column_by_name(report_column_name: str) -> Optional[ReportColumn]:
    if report_column := ReportColumn.objects(name=report_column_name, is_active=True).first():
        return report_column
    raise NotFoundError(
        f"Could not get report column with name = {report_column_name}. There is no such entity")
