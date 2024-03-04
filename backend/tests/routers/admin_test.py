import json

import pytest
from fastapi.testclient import TestClient
from main import app
from services.user import get_current_user
from tests.conftest import clean_up_test, connect_test

from tests.conftest import another_admin, create_admin_user

NEW_ADMIN_NAME = "New Admin Name"
NEW_PASSWORD = "NewAdminPa$$1"
ME_ENDPOINT = "/admin/me"
CREATE_ENDPOINT = "/admin/create"


@pytest.fixture(scope="function")
def client_setup():
    db_name = "test_db"
    connect_test(db_name)
    admin = create_admin_user()
    with TestClient(app) as test_client:
        yield test_client, admin
    clean_up_test(db_name)


def test_create_admin_success(client_setup):
    client, parent = client_setup
    app.dependency_overrides[get_current_user] = lambda: parent
    response = client.post(CREATE_ENDPOINT, json={"name": NEW_ADMIN_NAME,
                                                  "email": "new@admin.com",
                                                  "parent_admin": parent.id})
    assert response.status_code == 201
    assert response.json()['id'] is not None
    assert isinstance(response.json()['id'], int)


def test_create_admin_already_exists(client_setup):
    client, parent = client_setup
    app.dependency_overrides[get_current_user] = lambda: parent
    response = client.post(CREATE_ENDPOINT, json={"name": NEW_ADMIN_NAME,
                                                  "email": parent.email,
                                                  "parent_admin": parent.id})
    assert response.status_code == 400


def test_create_admin_not_found_parent(client_setup):
    client, parent = client_setup
    app.dependency_overrides[get_current_user] = lambda: parent
    response = client.post(CREATE_ENDPOINT, json={"name": NEW_ADMIN_NAME,
                                                  "email": "new@admin.com",
                                                  "parent_admin": parent.id + 100})
    assert response.status_code == 404


def test_delete_child_admin_success(client_setup):
    client, parent = client_setup
    app.dependency_overrides[get_current_user] = lambda: parent
    another_admin_entity = another_admin(parent_admin=parent).save()
    response = client.delete(f"/admin/{another_admin_entity.id}")
    assert response.status_code == 200


def test_delete_child_admin_not_found(client_setup):
    client, parent = client_setup
    app.dependency_overrides[get_current_user] = lambda: parent
    response = client.delete(f"/admin/{parent.id + 1000}")
    assert response.status_code == 404


def test_delete_child_admin_root_admin(client_setup):
    client, parent = client_setup
    app.dependency_overrides[get_current_user] = lambda: parent
    response = client.delete(f"/admin/{parent.id}")
    assert response.status_code == 403


def test_get_parent_children_success(client_setup):
    client, parent = client_setup
    app.dependency_overrides[get_current_user] = lambda: parent
    another_admin_entity = another_admin(parent_admin=parent).save()
    response = client.get("/admin/children")
    assert response.status_code == 200
    content = json.loads(response.json())
    assert len(content) == 1
    assert content[0]['_id'] == another_admin_entity.id


def test_get_parent_children_not_found(client_setup):
    client, parent = client_setup
    app.dependency_overrides[get_current_user] = lambda: parent
    parent.is_active = False
    parent.save()
    response = client.get("/admin/children")
    assert response.status_code == 404


def test_get_current_admin_success(client_setup):
    client, parent = client_setup
    app.dependency_overrides[get_current_user] = lambda: parent
    response = client.get(ME_ENDPOINT)
    assert response.status_code == 200
    content = json.loads(response.json())
    assert content['_id'] == parent.id


def test_get_current_admin_not_found(client_setup):
    client, parent = client_setup
    parent.is_active = False
    parent.save()
    app.dependency_overrides[get_current_user] = lambda: parent
    response = client.get(ME_ENDPOINT)
    assert response.status_code == 404


def test_get_admins_success(client_setup):
    client, parent = client_setup
    app.dependency_overrides[get_current_user] = lambda: parent
    response = client.get("/admin/")
    assert response.status_code == 200
    content = json.loads(response.json())
    assert len(content) == 1
    assert content[0]['_id'] == parent.id


def test_get_admins_not_found(client_setup):
    client, parent = client_setup
    parent.is_active = False
    parent.save()
    app.dependency_overrides[get_current_user] = lambda: parent
    response = client.get("/admin/")
    assert response.status_code == 404


def test_put_admin_success(client_setup):
    client, admin = client_setup
    app.dependency_overrides[get_current_user] = lambda: admin
    response = client.put(ME_ENDPOINT, json={"name": NEW_ADMIN_NAME,
                                             "password": NEW_PASSWORD,
                                             "password_confirm": NEW_PASSWORD})
    assert response.status_code == 200


def test_put_admin_not_found(client_setup):
    client, admin = client_setup
    admin.is_active = False
    admin.save()
    app.dependency_overrides[get_current_user] = lambda: admin
    response = client.put(ME_ENDPOINT, json={"name": NEW_ADMIN_NAME,
                                             "password": NEW_PASSWORD,
                                             "password_confirm": NEW_PASSWORD})
    assert response.status_code == 404


def test_put_admin_invalid_update(client_setup):
    client, admin = client_setup
    app.dependency_overrides[get_current_user] = lambda: admin
    response = client.put(ME_ENDPOINT, json={"name": NEW_ADMIN_NAME,
                                             "password": NEW_PASSWORD,
                                             "password_confirm": "WrongPa$$word1"})
    assert response.status_code == 400
