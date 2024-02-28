import json

import pytest
from mock import patch
from errors.forbidden import ForbiddenError
from models.admin import Admin
from models.role import Role
from services.admin import validate_parent, create_admin, delete_admin, delete_customer_by_admin, get_admin, \
    get_admin_children, get_admin_children_by_current_user, get_admins, update_admin
from tests.conftest import clean_up_test, connect_test, create_admin_user, another_customer, another_admin, \
    create_customer_user

from errors.not_found import NotFoundError

from schemas.admin import AdminCreate, AdminDelete, AdminUpdate

from errors.bad_request import BadRequestError

from services.utils import password_match_patterns

from models.customer import Customer


@pytest.fixture(scope="function")
def db_setup():
    db_name = "test_db"
    connect_test(db_name)
    admin_role = Role(name='Admin').save()
    parent_admin = Admin(name='Parent Admin', email='parent@admin.com', role=admin_role, password='hashed_pass',
                         is_active=True).save()
    yield parent_admin
    clean_up_test(db_name)


GET_CURRENT_USER_PATH = 'services.user.get_current_user'
GET_USER_BY_EMAIL_PATH = 'services.user.get_user_by_email'


def test_validate_parent_success(db_setup):
    parent_admin = db_setup
    with patch(GET_CURRENT_USER_PATH, return_value=parent_admin):
        try:
            validate_parent(parent_admin, parent_admin.id, "create")
        except Exception as e:
            pytest.fail(f"Unexpected error occurred: {e}")


def test_validate_parent_failure(db_setup):
    parent_admin = db_setup
    mock_admin = another_admin()
    with patch(GET_CURRENT_USER_PATH, return_value=mock_admin):
        with pytest.raises(ForbiddenError):
            validate_parent(mock_admin, parent_admin.id, "create")


def test_validate_parent_not_found_error(db_setup):
    non_existing_parent_admin_id = 99999
    parent_admin = db_setup
    with patch(GET_CURRENT_USER_PATH, return_value=parent_admin):
        with pytest.raises(NotFoundError):
            validate_parent(parent_admin, non_existing_parent_admin_id, "create")


def test_create_admin_parent_not_found_error(db_setup):
    parent_admin = db_setup
    admin_create_body = AdminCreate(name="Admin 2", email="new@admin.com", parent_admin=99999, password="password",
                                    confirm_password="password")

    with patch(GET_CURRENT_USER_PATH, return_value=parent_admin), pytest.raises(NotFoundError):
        create_admin(admin_create_body)


def test_create_admin_email_already_exists(db_setup):
    parent_admin = db_setup

    admin_create_body = AdminCreate(name="New Admin", email="parent@admin.com",
                                    parent_admin=parent_admin.id, password="password",
                                    confirm_password="password")

    with patch(GET_CURRENT_USER_PATH, return_value=parent_admin), \
            patch(GET_USER_BY_EMAIL_PATH,
                  return_value=another_admin()), \
            pytest.raises(BadRequestError):
        create_admin(admin_create_body, parent_admin)


def test_create_admin_success(db_setup):
    parent_admin = db_setup
    admin_create_body = AdminCreate(name="New Admin", email="new@admin.com",
                                    parent_admin=parent_admin.id, password="password",
                                    confirm_password="password")

    with patch(GET_CURRENT_USER_PATH, return_value=parent_admin):
        response = create_admin(admin_create_body, parent_admin)
        response_content = json.loads(response.body)
        assert password_match_patterns(response_content['admin_password'])


def test_delete_admin_success(db_setup):
    parent_admin = db_setup
    test_admin = another_admin(parent_admin).save()
    admin_delete = AdminDelete(admin_to_delete=test_admin.id)

    with patch(GET_CURRENT_USER_PATH, return_value=parent_admin):
        delete_admin(admin_delete, parent_admin)
        updated_admin = Admin.objects(id=test_admin.id).first()
        assert not updated_admin.is_active


def test_delete_admin_not_found(db_setup):
    parent_admin = db_setup
    admin_delete = AdminDelete(admin_to_delete=999)
    with patch(GET_CURRENT_USER_PATH, return_value=parent_admin), pytest.raises(NotFoundError):
        delete_admin(admin_delete, parent_admin)


def test_delete_no_parent(db_setup):
    core_admin = db_setup
    test_admin = another_admin().save()
    admin_delete = AdminDelete(admin_to_delete=test_admin.id)
    with patch(GET_CURRENT_USER_PATH, return_value=core_admin), pytest.raises(ForbiddenError):
        delete_admin(admin_delete, core_admin)


def test_delete_incorrect_parent(db_setup):
    core_admin = db_setup

    parent_admin = another_admin(core_admin).save()
    test_admin = another_admin(parent_admin).save()

    admin_delete = AdminDelete(admin_to_delete=test_admin.id)
    with patch(GET_CURRENT_USER_PATH, return_value=core_admin), pytest.raises(ForbiddenError):
        delete_admin(admin_delete, core_admin)


def test_delete_customer_by_admin(db_setup):
    admin = db_setup
    customer = create_customer_user()
    with patch(GET_CURRENT_USER_PATH, return_value=admin):
        delete_customer_by_admin(customer.id, admin)
        deleted_customer = Customer.objects(id=customer.id).first()
        assert not deleted_customer.is_active


def test_delete_customer_by_invalid_admin(db_setup):
    admin = db_setup
    admin.is_active = False
    admin.save()
    customer = create_customer_user()
    with patch(GET_CURRENT_USER_PATH, return_value=admin), pytest.raises(NotFoundError):
        delete_customer_by_admin(customer.id, admin)
        not_deleted_customer = Customer.objects(id=customer.id).first()
        assert not_deleted_customer.is_active


def test_delete_customer_by_another_customer(db_setup):
    customer = create_customer_user()
    another_customer_entity = another_customer().save()
    with patch(GET_CURRENT_USER_PATH, return_value=another_customer_entity), pytest.raises(NotFoundError):
        delete_customer_by_admin(customer.id, another_customer_entity)
        not_deleted_customer = Customer.objects(id=customer.id).first()
        assert not_deleted_customer.is_active


def test_delete_not_found_customer_by_admin(db_setup):
    admin = db_setup
    customer = create_customer_user()
    with patch(GET_CURRENT_USER_PATH, return_value=admin), pytest.raises(NotFoundError):
        delete_customer_by_admin(customer.id + 1000, admin)


def test_get_admin_success(db_setup):
    parent_admin = db_setup
    result = get_admin(parent_admin.id)
    assert result is not None
    assert result.id == parent_admin.id


def test_get_admin_not_found(db_setup):
    with pytest.raises(NotFoundError):
        get_admin(999)


def test_get_admin_children_by_current_user_success(db_setup):
    parent_admin = db_setup
    test_admin = another_admin(parent_admin).save()

    with patch(GET_CURRENT_USER_PATH, return_value=parent_admin):
        result = get_admin_children_by_current_user(parent_admin)
        assert len(result) == 1
        assert result[0].id == test_admin.id


def test_get_admin_children_by_current_user_inactive(db_setup):
    parent_admin = db_setup
    test_admin = another_admin(parent_admin)
    test_admin.is_active = False
    test_admin.save()

    with patch(GET_CURRENT_USER_PATH, return_value=parent_admin):
        result = get_admin_children_by_current_user(parent_admin)
        assert len(result) == 0


def test_get_admin_children_success(db_setup):
    parent_admin = db_setup
    test_admin = another_admin(parent_admin).save()

    result = get_admin_children(parent_admin)
    assert len(result) == 1
    assert result[0].id == test_admin.id


def test_get_admin_children_inactive(db_setup):
    parent_admin = db_setup
    test_admin = another_admin(parent_admin)
    test_admin.is_active = False
    test_admin.save()

    result = get_admin_children(parent_admin)
    assert len(result) == 0


def test_get_admins_success(db_setup):
    parent_admin = db_setup
    child_admin_entity = another_admin(parent_admin).save()
    another_admin_entity = another_admin().save()

    result = get_admins()
    assert len(result) == 3
    result_ids = list(map(lambda admin: admin.id, result))
    assert [parent_admin.id, child_admin_entity.id, another_admin_entity.id] == result_ids


def test_get_admins_inactive(db_setup):
    parent_admin = db_setup
    test_admin = another_admin(parent_admin)
    test_admin.is_active = False
    test_admin.save()

    result = get_admins()
    assert len(result) == 1
    assert result[0].id == parent_admin.id


def test_update_admin_success(db_setup):
    another_admin_entity = another_admin().save()
    old_password = another_admin_entity.password
    admin_update = AdminUpdate(name="New Name", password="NewPassword?1", password_confirm="NewPassword?1")

    with patch(GET_CURRENT_USER_PATH, return_value=another_admin_entity):
        update_admin(admin_update, another_admin_entity)

        updated_admin = Admin.objects(id=another_admin_entity.id).first()
        assert updated_admin.name == "New Name"
        assert old_password != updated_admin.password


def test_update_admin_password_mismatch(db_setup):
    another_admin_entity = another_admin().save()
    old_password = another_admin_entity.password
    admin_update = AdminUpdate(password="Password?1", password_confirm="DifferentPassword2!")

    with patch(GET_CURRENT_USER_PATH, return_value=another_admin_entity), pytest.raises(BadRequestError):
        update_admin(admin_update, another_admin_entity)
        updated_admin = Admin.objects(id=another_admin_entity.id).first()
        assert old_password == updated_admin.password


def test_update_admin_password_mismatch_correct_name(db_setup):
    another_admin_entity = another_admin().save()
    old_password = another_admin_entity.password
    old_name = another_admin_entity.name
    admin_update = AdminUpdate(name="New admin name", password="Password?1", password_confirm="DifferentPassword2!")

    with patch(GET_CURRENT_USER_PATH, return_value=another_admin_entity), pytest.raises(BadRequestError):
        update_admin(admin_update, another_admin_entity)
        updated_admin = Admin.objects(id=another_admin_entity.id).first()
        assert old_password == updated_admin.password
        assert old_name == updated_admin.name
