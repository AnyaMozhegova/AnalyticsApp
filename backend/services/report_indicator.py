from typing import Optional

from errors.not_found import NotFoundError
from models.report_indicator import ReportIndicator
from schemas.report_indicator import ReportIndicatorUpdate
from services.utils import check_admin_access


def get_report_indicators(user_id: int):
    check_admin_access(user_id)
    return ReportIndicator.objects()


def get_report_indicator(user_id: int, report_indicator_id: int) -> Optional[ReportIndicator]:
    check_admin_access(user_id)
    if report_indicator := ReportIndicator.objects(id=report_indicator_id).first():
        return report_indicator
    raise NotFoundError(
        f"Could not get report_indicator with id = {report_indicator_id}. There is no such entity")


def get_report_indicator_by_name(user_id: int, report_indicator_name: str) -> Optional[ReportIndicator]:
    check_admin_access(user_id)
    if report_indicator := ReportIndicator.objects(name=report_indicator_name).first():
        return report_indicator
    raise NotFoundError(
        f"Could not get report_indicator with name = {report_indicator_name}. There is no such entity")


def update_report_indicator(user_id: int, report_indicator_id: int, report_indicator_body: ReportIndicatorUpdate) -> \
        Optional[ReportIndicator]:
    check_admin_access(user_id)
    if report_indicator := ReportIndicator.objects(id=report_indicator_id).first():
        for field, value in report_indicator_body.dict(exclude_unset=True).items():
            setattr(report_indicator, field, value)
        report_indicator.save()
        return report_indicator
    raise NotFoundError(f"Could not get report_indicator with id = {report_indicator_id}. There is no such entity")
