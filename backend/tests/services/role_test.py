import pytest
from errors.forbidden import ForbiddenError
from errors.not_found import NotFoundError
from mongoengine import NotUniqueError

from models.role import Role
from schemas.role import RoleUpdate
from services.role import get_role, get_role_by_name, get_roles, update_role

from tests.conftest import clean_up_test, connect_test, create_admin_user

ROLE_1_NAME = "Role_1"
ROLE_2_NAME = "Role_2"


@pytest.fixture(scope="function")
def db_setup():
    db_name = "test_db"
    connect_test(db_name)
    user = create_admin_user()
    role = Role(name=ROLE_1_NAME).save()
    yield role, user
    clean_up_test(db_name)


def test_get_roles(db_setup):
    _, admin_user = db_setup
    roles = get_roles(user_id=admin_user.id)
    assert len(roles) == 2  # With admin role


def test_get_role(db_setup):
    role, admin_user = db_setup
    result = get_role(user_id=admin_user.id, role_id=role.id)
    assert result['name'] == ROLE_1_NAME


def test_get_role_by_name(db_setup):
    role, admin_user = db_setup
    result = get_role_by_name(user_id=admin_user.id, role_name=ROLE_1_NAME)
    assert result['id'] == role.id


def test_get_role_non_existent_id(db_setup):
    non_existent_id = 999
    _, admin_user = db_setup

    with pytest.raises(NotFoundError):
        get_role(user_id=admin_user.id, role_id=non_existent_id)


def test_get_role_by_name_non_existent(db_setup):
    non_existent_name = "NonExistentName"
    _, admin_user = db_setup

    with pytest.raises(NotFoundError):
        get_role_by_name(user_id=admin_user.id, role_name=non_existent_name)


def test_update_role(db_setup):
    role, admin_user = db_setup
    update_data = RoleUpdate(name=ROLE_2_NAME)
    updated_role = update_role(user_id=admin_user.id, role_id=role.id,
                               role_update=update_data)
    assert updated_role.name == ROLE_2_NAME


def test_update_role_non_existent_id(db_setup):
    _, admin_user = db_setup
    non_existent_id = 999
    update_data = RoleUpdate(name=ROLE_2_NAME)

    with pytest.raises(NotFoundError):
        update_role(user_id=admin_user.id, role_id=non_existent_id,
                    role_update=update_data)


def test_update_role_duplicated_name(db_setup):
    _, admin_user = db_setup
    role = Role(name=ROLE_2_NAME).save()
    update_data = RoleUpdate(name=ROLE_1_NAME)

    with pytest.raises(NotUniqueError):
        update_role(user_id=admin_user.id, role_id=role.id,
                    role_update=update_data)


def test_unauthorized_access(mocker, db_setup):
    mocker.patch('services.utils.check_admin_access', side_effect=ForbiddenError("User doesn't have admin access"))
    _, admin_user = db_setup
    with pytest.raises(ForbiddenError):
        get_roles(user_id=admin_user.id + 1)
