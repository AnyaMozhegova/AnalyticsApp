from errors.not_found import NotFoundError
from services.utils import models_to_dict

from models.report_indicator import ReportIndicator
from schemas.report_indicator import ReportIndicatorCreate, ReportIndicatorUpdate
from services.utils import check_admin_access


def create_report_indicator(user_id: int, report_indicator_create: ReportIndicatorCreate) -> int:
    check_admin_access(user_id)
    report_indicator = ReportIndicator(name=report_indicator_create.name)
    report_indicator.save()
    return report_indicator.id


def delete_report_indicator(user_id: int, report_indicator_id: int):
    check_admin_access(user_id)
    if report_indicator := ReportIndicator.objects(id=report_indicator_id).first():
        report_indicator.delete()
    else:
        raise NotFoundError(
            f"Could not delete report indicator with id = {report_indicator_id}. There is no such entity")


def get_report_indicators(user_id: int):
    check_admin_access(user_id)
    report_indicators = ReportIndicator.objects()
    return models_to_dict(report_indicators)


def get_report_indicator(user_id: int, report_indicator_id: int):
    check_admin_access(user_id)
    if report_indicator := ReportIndicator.objects(id=report_indicator_id).first():
        return report_indicator.to_dict()
    raise NotFoundError(
        f"Could not get report_indicator with id = {report_indicator_id}. There is no such entity")


def get_report_indicator_by_name(user_id: int, report_indicator_name: str):
    check_admin_access(user_id)
    if report_indicator := ReportIndicator.objects(name=report_indicator_name).first():
        return report_indicator.to_dict()
    raise NotFoundError(
        f"Could not get report_indicator with name = {report_indicator_name}. There is no such entity")


def update_report_indicator(user_id: int, report_indicator_id: int, report_indicator_body: ReportIndicatorUpdate):
    check_admin_access(user_id)
    if report_indicator := ReportIndicator.objects(id=report_indicator_id).first():
        for field, value in report_indicator_body.dict(exclude_unset=True).items():
            setattr(report_indicator, field, value)
        report_indicator.save()
        return report_indicator
    raise NotFoundError(f"Could not get report_indicator with id = {report_indicator_id}. There is no such entity")
