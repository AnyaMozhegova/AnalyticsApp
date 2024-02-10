import pytest
from errors.forbidden import ForbiddenError
from errors.not_found import NotFoundError
from models.report_indicator import ReportIndicator
from mongoengine import NotUniqueError
from schemas.report_indicator import ReportIndicatorCreate, ReportIndicatorUpdate
from services.report_indicator import (get_report_indicator, get_report_indicators, update_report_indicator,
                                       get_report_indicator_by_name)

INDICATOR_1_NAME = "Indicator_1"
INDICATOR_2_NAME = "Indicator_2"


def create_indicator_utils(indicator_name):
    report_indicator = ReportIndicator(name=indicator_name).save()
    return report_indicator.id


def test_get_report_indicators(admin_user):
    create_indicator_utils(INDICATOR_1_NAME)
    create_indicator_utils(INDICATOR_2_NAME)
    indicators = get_report_indicators(user_id=admin_user.id)
    assert len(indicators) == 2


def test_get_report_indicators_empty_database(admin_user):
    result = get_report_indicators(admin_user.id)
    assert len(result) == 0, "Expected an empty list when no report indicators exist"


def test_get_report_indicator(admin_user):
    report_indicator_id = create_indicator_utils(INDICATOR_1_NAME)
    result: ReportIndicator = get_report_indicator(user_id=admin_user.id, report_indicator_id=report_indicator_id)
    assert result.name == INDICATOR_1_NAME


def test_get_report_indicator_by_name(admin_user):
    report_indicator_id = create_indicator_utils(INDICATOR_1_NAME)
    result: ReportIndicator = get_report_indicator_by_name(user_id=admin_user.id,
                                                           report_indicator_name=INDICATOR_1_NAME)
    assert result.id == report_indicator_id


def test_get_report_indicator_non_existent_id(admin_user):
    non_existent_id = 999

    with pytest.raises(NotFoundError):
        get_report_indicator(user_id=admin_user.id, report_indicator_id=non_existent_id)


def test_get_report_indicator_by_name_non_existent(admin_user):
    non_existent_name = "NonExistentName"

    with pytest.raises(NotFoundError):
        get_report_indicator_by_name(user_id=admin_user.id, report_indicator_name=non_existent_name)


def test_update_report_indicator(admin_user):
    report_indicator_id = create_indicator_utils(INDICATOR_1_NAME)
    update_data = ReportIndicatorUpdate(name=INDICATOR_2_NAME)
    updated_indicator = update_report_indicator(user_id=admin_user.id, report_indicator_id=report_indicator_id,
                                                report_indicator_body=update_data)
    assert updated_indicator.name == INDICATOR_2_NAME


def test_update_report_indicator_non_existent_id(admin_user):
    non_existent_id = 999
    update_data = ReportIndicatorUpdate(name=INDICATOR_2_NAME)

    with pytest.raises(NotFoundError):
        update_report_indicator(user_id=admin_user.id, report_indicator_id=non_existent_id,
                                report_indicator_body=update_data)


def test_update_report_indicator_duplicated_name(admin_user):
    create_indicator_utils(INDICATOR_1_NAME)
    report_indicator_id = create_indicator_utils(INDICATOR_2_NAME)
    update_data = ReportIndicatorUpdate(name=INDICATOR_1_NAME)

    with pytest.raises(NotUniqueError):
        update_report_indicator(user_id=admin_user.id, report_indicator_id=report_indicator_id,
                                report_indicator_body=update_data)


def test_unauthorized_access(mocker, admin_user):
    mocker.patch('services.utils.check_admin_access',
                 side_effect=ForbiddenError("User doesn't have admin access"))
    with pytest.raises(ForbiddenError):
        get_report_indicators(user_id=admin_user.id + 1)
