import json

import pytest
from errors.bad_request import BadRequestError
from errors.not_found import NotFoundError
from mock import patch
from models.customer import Customer
from models.role import Role
from schemas.customer import CustomerCreate, CustomerUpdate
from services.customer import create_customer, delete_customer, get_current_customer, get_customer, get_customers, \
    update_customer, delete_customer_by_admin
from tests.conftest import clean_up_test, connect_test, another_customer, create_admin_user, another_admin


@pytest.fixture(scope="function")
def db_setup():
    db_name = "test_db"
    connect_test(db_name)
    customer_role = Role(name='Customer').save()
    customer = Customer(name='Test Customer', email='customer@gmail.com', role=customer_role, password='hashed_pass',
                        is_active=True).save()
    yield customer
    clean_up_test(db_name)


GET_CURRENT_USER_PATH = 'services.user.get_current_user'
GET_USER_BY_EMAIL_PATH = 'services.user.get_user_by_email'
CORRECT_PASSWORD = "MyPassword!?1"


def test_create_customer_email_already_exists(db_setup):
    existing_customer = db_setup

    customer_create_body = CustomerCreate(name="Customer 2", email=existing_customer.email, password=CORRECT_PASSWORD,
                                          password_confirm=CORRECT_PASSWORD)

    with pytest.raises(BadRequestError):
        create_customer(customer_create_body)


def test_create_customer_password_mismatch(db_setup):
    customer_create_body = CustomerCreate(name="Customer 3", email="new_customer@gmail.com", password=CORRECT_PASSWORD,
                                          password_confirm="anpassworD?1")
    with pytest.raises(BadRequestError):
        create_customer(customer_create_body)


def test_create_customer_success(db_setup):
    customer_email = "new@customer.com"
    customer_create_body = CustomerCreate(name="New Customer", email=customer_email, password=CORRECT_PASSWORD,
                                          password_confirm=CORRECT_PASSWORD)

    response = create_customer(customer_create_body)
    content = json.loads(response.body)
    created_customer = Customer.objects(is_active=True, id=content['id']).first()
    assert created_customer.email == customer_email


def test_delete_customer_success(db_setup):
    customer = db_setup

    with patch(GET_CURRENT_USER_PATH, return_value=customer):
        delete_customer(customer)
        deleted_customer = Customer.objects(id=customer.id).first()
        assert not deleted_customer.is_active


def test_delete_customer_not_found(db_setup):
    customer = db_setup
    customer.is_active = False
    customer.save()
    with patch(GET_CURRENT_USER_PATH, return_value=customer), pytest.raises(NotFoundError):
        delete_customer(customer)


def test_delete_customer_by_admin(db_setup):
    customer = db_setup
    admin = create_admin_user()
    with patch(GET_CURRENT_USER_PATH, return_value=admin):
        delete_customer_by_admin(customer.id, admin)
        deleted_customer = Customer.objects(id=customer.id).first()
        assert not deleted_customer.is_active


def test_delete_customer_by_invalid_admin(db_setup):
    customer = db_setup
    admin = another_admin(parent_admin=None, is_active=False)
    with patch(GET_CURRENT_USER_PATH, return_value=admin), pytest.raises(NotFoundError):
        delete_customer_by_admin(customer.id, admin)
        not_deleted_customer = Customer.objects(id=customer.id).first()
        assert not_deleted_customer.is_active


def test_delete_customer_by_another_customer(db_setup):
    customer = db_setup
    another_customer_entity = another_customer().save()
    with patch(GET_CURRENT_USER_PATH, return_value=another_customer_entity), pytest.raises(NotFoundError):
        delete_customer_by_admin(customer.id, another_customer_entity)
        not_deleted_customer = Customer.objects(id=customer.id).first()
        assert not_deleted_customer.is_active


def test_delete_not_found_customer_by_admin(db_setup):
    customer = db_setup
    admin = create_admin_user()
    with patch(GET_CURRENT_USER_PATH, return_value=admin), pytest.raises(NotFoundError):
        delete_customer_by_admin(customer.id + 1000, admin)


def test_get_customer_success(db_setup):
    customer = db_setup
    result = get_customer(customer.id)
    assert result is not None
    assert result.id == customer.id


def test_get_customer_not_found(db_setup):
    with pytest.raises(NotFoundError):
        get_customer(999)


def test_get_current_customer_success(db_setup):
    customer = db_setup
    with patch(GET_CURRENT_USER_PATH, return_value=customer):
        result = get_current_customer(customer)
        assert result is not None
        assert result.id == customer.id


def test_get_current_customer_not_found(db_setup):
    new_customer = another_customer()
    with patch(GET_CURRENT_USER_PATH, return_value=new_customer), pytest.raises(NotFoundError):
        get_current_customer(new_customer)


def test_get_customers_success(db_setup):
    customer = db_setup
    another_customer_entity = another_customer().save()
    admin = another_admin().save()

    result = get_customers(admin)
    assert len(result) == 2
    result_ids = list(map(lambda customer_entity: customer_entity.id, result))
    assert [customer.id, another_customer_entity.id] == result_ids


def test_get_customers_inactive(db_setup):
    customer = db_setup
    another_customer(False)
    admin = another_admin().save()

    result = get_customers(admin)
    assert len(result) == 1
    assert result[0].id == customer.id


def test_get_customers_by_customer(db_setup):
    another_customer_entity = another_customer()

    with patch(GET_CURRENT_USER_PATH, return_value=another_customer_entity), pytest.raises(NotFoundError):
        get_customers(another_customer_entity)


def test_update_customer_success(db_setup):
    customer = db_setup
    old_password = customer.password
    customer_update = CustomerUpdate(name="New Name", password="NewPassword?1", password_confirm="NewPassword?1")

    with patch(GET_CURRENT_USER_PATH, return_value=customer):
        update_customer(customer_update, customer)

        updated_customer = Customer.objects(id=customer.id).first()
        assert updated_customer.name == "New Name"
        assert old_password != updated_customer.password


def test_update_customer_password_mismatch(db_setup):
    customer = db_setup
    old_password = customer.password
    customer_update = CustomerUpdate(password="Password?1", password_confirm="DifferentPassword2!")

    with patch(GET_CURRENT_USER_PATH, return_value=customer), pytest.raises(BadRequestError):
        update_customer(customer_update, customer)
        updated_customer = Customer.objects(id=customer.id).first()
        assert old_password == updated_customer.password


def test_update_customer_password_mismatch_correct_name(db_setup):
    customer = db_setup
    old_password = customer.password
    old_name = customer.name
    customer_update = CustomerUpdate(name="New customer name", password="Password?1",
                                     password_confirm="DifferentPassword2!")

    with patch(GET_CURRENT_USER_PATH, return_value=customer), pytest.raises(BadRequestError):
        update_customer(customer_update, customer)
        updated_customer = Customer.objects(id=customer.id).first()
        assert old_password == updated_customer.password
        assert old_name == updated_customer.name
