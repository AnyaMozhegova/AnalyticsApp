import pytest
from errors.forbidden import ForbiddenError
from errors.not_found import NotFoundError
from mongoengine import NotUniqueError
from schemas.report_indicator import ReportIndicatorUpdate
from services.report_indicator import (get_report_indicator, get_report_indicator_by_name, get_report_indicators_by_admin,
                                       update_report_indicator)
from tests.conftest import clean_up_test, connect_test, create_admin_user

from models.report_indicator import ReportIndicator

INDICATOR_1_NAME = "Indicator_1"
INDICATOR_2_NAME = "Indicator_2"


@pytest.fixture(scope="function")
def db_setup():
    db_name = "test_db"
    connect_test(db_name)
    user = create_admin_user()
    report_indicator_1 = ReportIndicator(name=INDICATOR_1_NAME).save()
    report_indicator_2 = ReportIndicator(name=INDICATOR_2_NAME).save()
    yield report_indicator_1, report_indicator_2, user
    clean_up_test(db_name)


def test_get_report_indicators(db_setup):
    _, _, admin_user = db_setup
    indicators = get_report_indicators_by_admin(user_id=admin_user.id)
    print([indicator.to_dict() for indicator in indicators])
    assert len(indicators) == 2


def test_get_report_indicators_empty_database(db_setup):
    report_indicator_1, report_indicator_2, admin_user = db_setup
    report_indicator_1.delete()
    report_indicator_2.delete()
    result = get_report_indicators_by_admin(admin_user.id)
    assert len(result) == 0, "Expected an empty list when no report indicators exist"


def test_get_report_indicator(db_setup):
    report_indicator_1, _, admin_user = db_setup
    result: ReportIndicator = get_report_indicator(user_id=admin_user.id, report_indicator_id=report_indicator_1.id)
    assert result.name == INDICATOR_1_NAME


def test_get_report_indicator_by_name(db_setup):
    report_indicator_1, _, admin_user = db_setup
    result: ReportIndicator = get_report_indicator_by_name(user_id=admin_user.id,
                                                           report_indicator_name=INDICATOR_1_NAME)
    assert result.id == report_indicator_1.id


def test_get_report_indicator_non_existent_id(db_setup):
    non_existent_id = 999
    _, _, admin_user = db_setup

    with pytest.raises(NotFoundError):
        get_report_indicator(user_id=admin_user.id, report_indicator_id=non_existent_id)


def test_get_report_indicator_by_name_non_existent(db_setup):
    non_existent_name = "NonExistentName"
    _, _, admin_user = db_setup

    with pytest.raises(NotFoundError):
        get_report_indicator_by_name(user_id=admin_user.id, report_indicator_name=non_existent_name)


def test_update_report_indicator(db_setup):
    report_indicator_1, _, admin_user = db_setup
    new_name = "New Report Indicator"
    update_data = ReportIndicatorUpdate(name=new_name)
    updated_indicator = update_report_indicator(user_id=admin_user.id, report_indicator_id=report_indicator_1.id,
                                                report_indicator_body=update_data)
    assert updated_indicator.name == new_name


def test_update_report_indicator_non_existent_id(db_setup):
    non_existent_id = 999
    update_data = ReportIndicatorUpdate(name="New Report Indicator")
    _, _, admin_user = db_setup

    with pytest.raises(NotFoundError):
        update_report_indicator(user_id=admin_user.id, report_indicator_id=non_existent_id,
                                report_indicator_body=update_data)


def test_update_report_indicator_duplicated_name(db_setup):
    _, report_indicator_2, admin_user = db_setup
    print(ReportIndicator.objects(id=report_indicator_2.id).first().to_dict())
    update_data = ReportIndicatorUpdate(name=INDICATOR_1_NAME)

    with pytest.raises(NotUniqueError):
        update_report_indicator(user_id=admin_user.id, report_indicator_id=report_indicator_2.id,
                                report_indicator_body=update_data)


def test_unauthorized_access(mocker, db_setup):
    mocker.patch('services.utils.check_admin_access',
                 side_effect=ForbiddenError("User doesn't have admin access"))
    _, _, admin_user = db_setup
    with pytest.raises(ForbiddenError):
        get_report_indicators_by_admin(user_id=admin_user.id + 1)
