import json
import os
import shutil
from unittest.mock import Mock

import pandas as pd
import pytest
from fastapi import UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
from main import app
from models.customer import Customer
from models.role import Role
from services.user import get_current_user
from tests.conftest import clean_up_test, connect_test, create_customer_user, create_admin_user


def not_found_customer():
    customer_role = Role.objects(name="Customer").first()
    return Customer(name='customer_user', email="customer@gmail.com", password="customer_password!123",
                    role=customer_role)


def mock_oauth_form():
    mock_form = Mock(spec=OAuth2PasswordRequestForm)
    mock_form.username = "customer@gmail.com"
    mock_form.password = "customer_password!123"
    return mock_form


def create_upload_file(filename: str, data: pd.DataFrame) -> UploadFile:
    file_path = f'tests/{filename}'
    data.to_excel(file_path, index=False)
    return UploadFile(filename=filename, file=open(file_path, 'rb'))


def cleanup_files():
    shutil.rmtree('user_data', ignore_errors=True)
    for file in os.listdir('tests'):
        if file.endswith(".xls") or file.endswith(".xlsx"):
            os.remove(os.path.join('tests', file))


NEW_CUSTOMER_NAME = "New Customer Name"
NEW_PASSWORD = "NewPa$$word1"
ME_ENDPOINT = "/customer/me"
SIGN_UP_ENDPOINT = "/customer/sign_up"
UPLOAD_ENDPOINT = "/customer/upload_report"


@pytest.fixture(scope="function")
def client_setup():
    db_name = "test_db"
    connect_test(db_name)
    customer = create_customer_user()
    with TestClient(app) as test_client:
        yield test_client, customer
    clean_up_test(db_name)


def test_login_for_access_token(client_setup):
    client, user = client_setup
    app.dependency_overrides[OAuth2PasswordRequestForm] = mock_oauth_form
    response = client.post("/login")
    assert response.status_code == 200
    assert response.json()['id'] == user.id


def test_sign_up_customer_success(client_setup):
    client, _ = client_setup
    response = client.post(SIGN_UP_ENDPOINT, json={"name": "test customer",
                                                   "email": "testcustomer@gmail.com",
                                                   "password": NEW_PASSWORD,
                                                   "password_confirm": NEW_PASSWORD})
    assert response.status_code == 201
    assert response.json()['id'] is not None
    assert isinstance(response.json()['id'], int)


def test_sign_up_customer_already_exists(client_setup):
    client, user = client_setup
    response = client.post(SIGN_UP_ENDPOINT, json={"name": "Existed customer",
                                                   "email": user.email,
                                                   "password": NEW_PASSWORD,
                                                   "password_confirm": NEW_PASSWORD})
    assert response.status_code == 400


def test_sign_up_customer_invalid_create(client_setup):
    client, _ = client_setup
    response = client.post(SIGN_UP_ENDPOINT, json={"name": "Invalid customer",
                                                   "email": "testcustomer@gmail.com",
                                                   "password": NEW_PASSWORD,
                                                   "password_confirm": "WrongPa$$word1"})
    assert response.status_code == 400


def test_get_customer_success(client_setup):
    client, user = client_setup
    app.dependency_overrides[get_current_user] = lambda: user
    response = client.get(ME_ENDPOINT)
    assert response.status_code == 200
    report_response = json.loads(response.json())
    assert report_response['_id'] == user.id


def test_get_customer_not_found(client_setup):
    client, _ = client_setup
    app.dependency_overrides[get_current_user] = not_found_customer
    response = client.get(ME_ENDPOINT)
    assert response.status_code == 404


def test_delete_customer_success(client_setup):
    client, user = client_setup
    app.dependency_overrides[get_current_user] = lambda: user
    response = client.delete(ME_ENDPOINT)
    assert response.status_code == 200


def test_delete_customer_not_found(client_setup):
    client, _ = client_setup
    app.dependency_overrides[get_current_user] = not_found_customer
    response = client.delete(ME_ENDPOINT)
    assert response.status_code == 404


def test_delete_customer_by_admin_success(client_setup):
    client, user = client_setup
    admin = create_admin_user()
    app.dependency_overrides[get_current_user] = lambda: admin
    response = client.delete(f"customer/{user.id}")
    assert response.status_code == 200


def test_delete_customer_by_admin_not_found(client_setup):
    client, user = client_setup
    admin = create_admin_user()
    app.dependency_overrides[get_current_user] = lambda: admin
    response = client.delete(f"customer/{user.id + 100}")
    assert response.status_code == 404


def test_get_customers_by_admin_success(client_setup):
    client, user = client_setup
    admin = create_admin_user()
    app.dependency_overrides[get_current_user] = lambda: admin
    response = client.get("/customer/")
    assert response.status_code == 200
    content = json.loads(response.json())
    assert len(content) == 1
    assert content[0]["_id"] == user.id


def test_get_customers_by_admin_not_found(client_setup):
    client, _ = client_setup
    admin = create_admin_user()
    admin.is_active = False
    admin.save()
    app.dependency_overrides[get_current_user] = lambda: admin
    response = client.get("customer/")
    assert response.status_code == 404


def test_put_customer_success(client_setup):
    client, user = client_setup
    app.dependency_overrides[get_current_user] = lambda: user
    response = client.put(ME_ENDPOINT, json={"name": NEW_CUSTOMER_NAME,
                                             "password": NEW_PASSWORD,
                                             "password_confirm": NEW_PASSWORD})
    assert response.status_code == 200


def test_put_customer_not_found(client_setup):
    client, _ = client_setup
    app.dependency_overrides[get_current_user] = not_found_customer
    response = client.put(ME_ENDPOINT, json={"name": NEW_CUSTOMER_NAME,
                                             "password": NEW_PASSWORD,
                                             "password_confirm": NEW_PASSWORD})
    assert response.status_code == 404


def test_put_customer_invalid_update(client_setup):
    client, user = client_setup
    app.dependency_overrides[get_current_user] = lambda: user
    response = client.put(ME_ENDPOINT, json={"name": NEW_CUSTOMER_NAME,
                                             "password": NEW_PASSWORD,
                                             "password_confirm": "WrongPa$$word1"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_report_success(client_setup):
    client, user = client_setup
    app.dependency_overrides[get_current_user] = lambda: user
    data = pd.DataFrame({'A': [1, 2, 3, 4, 7, 7], 'B': [4, 5, 6, 7, 7, 7]})
    file = create_upload_file("valid.xlsx", data)
    response = client.post(UPLOAD_ENDPOINT,
                           files={"report": (file.filename, file.file, file.content_type)})
    assert response.status_code == 200
    cleanup_files()


@pytest.mark.asyncio
async def test_upload_report_customer_not_found(client_setup):
    client, _ = client_setup
    app.dependency_overrides[get_current_user] = not_found_customer
    data = pd.DataFrame({'A': [1, 2, 3, 4, 7, 7], 'B': [4, 5, 6, 7, 7, 7]})
    file = create_upload_file("valid.xlsx", data)
    response = client.post(UPLOAD_ENDPOINT,
                           files={"report": (file.filename, file.file, file.content_type)})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_upload_report_invalid_data(client_setup):
    client, user = client_setup
    app.dependency_overrides[get_current_user] = lambda: user
    data = pd.DataFrame({' ': [1, 2, 3, 4], 'B': [4, 5, 6, 7]})
    file = create_upload_file("invalid.xlsx", data)
    response = client.post(UPLOAD_ENDPOINT,
                           files={"report": (file.filename, file.file, file.content_type)})
    assert response.status_code == 400
