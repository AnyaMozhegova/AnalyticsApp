import pytest
from errors.forbidden import ForbiddenError
from errors.not_found import NotFoundError
from mongoengine import NotUniqueError

from models.role import Role
from schemas.role import RoleUpdate
from services.role import get_role, get_role_by_name, get_roles, update_role

ROLE_1_NAME = "Role_1"
ROLE_2_NAME = "Role_2"


def create_role_utils(role_name):
    role = Role(name=role_name).save()
    return role.id


def test_create_role(admin_user):
    role_id = create_role_utils(ROLE_1_NAME)
    assert role_id is not None
    assert Role.objects(name=ROLE_1_NAME).first() is not None


def test_create_role_duplicate_name(admin_user):
    create_role_utils(ROLE_1_NAME)
    with pytest.raises(NotUniqueError):
        create_role_utils(ROLE_1_NAME)


def test_get_roles(admin_user):
    create_role_utils(ROLE_1_NAME)
    create_role_utils(ROLE_2_NAME)
    roles = get_roles(user_id=admin_user.id)
    assert len(roles) == 3  # With admin role


def test_get_role(admin_user):
    role_id = create_role_utils(ROLE_1_NAME)
    result = get_role(user_id=admin_user.id, role_id=role_id)
    assert result['name'] == ROLE_1_NAME


def test_get_role_by_name(admin_user):
    role_id = create_role_utils(ROLE_1_NAME)
    result = get_role_by_name(user_id=admin_user.id, role_name=ROLE_1_NAME)
    assert result['id'] == role_id


def test_get_role_non_existent_id(admin_user):
    non_existent_id = 999

    with pytest.raises(NotFoundError):
        get_role(user_id=admin_user.id, role_id=non_existent_id)


def test_get_role_by_name_non_existent(admin_user):
    non_existent_name = "NonExistentName"

    with pytest.raises(NotFoundError):
        get_role_by_name(user_id=admin_user.id, role_name=non_existent_name)


def test_update_role(admin_user):
    role_id = create_role_utils(ROLE_1_NAME)
    update_data = RoleUpdate(name=ROLE_2_NAME)
    updated_role = update_role(user_id=admin_user.id, role_id=role_id,
                               role_update=update_data)
    assert updated_role.name == ROLE_2_NAME


def test_update_role_non_existent_id(admin_user):
    non_existent_id = 999
    update_data = RoleUpdate(name=ROLE_2_NAME)

    with pytest.raises(NotFoundError):
        update_role(user_id=admin_user.id, role_id=non_existent_id,
                    role_update=update_data)


def test_update_role_duplicated_name(admin_user):
    create_role_utils(ROLE_1_NAME)
    role_id = create_role_utils(ROLE_2_NAME)
    update_data = RoleUpdate(name=ROLE_1_NAME)

    with pytest.raises(NotUniqueError):
        update_role(user_id=admin_user.id, role_id=role_id,
                    role_update=update_data)


def test_unauthorized_access(mocker, admin_user):
    mocker.patch('services.utils.check_admin_access', side_effect=ForbiddenError("User doesn't have admin access"))
    with pytest.raises(ForbiddenError):
        get_roles(user_id=admin_user.id + 1)
