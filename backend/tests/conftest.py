from typing import Optional

import pytest
from fastapi.testclient import TestClient
from main import app
from models.admin import Admin
from models.customer import Customer
from models.role import Role
from mongoengine import get_connection
from services.user import get_password_hash


@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client


import mongomock
from mongoengine import connect, disconnect


def connect_test(db_name):
    disconnect(alias="default")
    connect(db_name, alias="default", mongo_client_class=mongomock.MongoClient)


def clean_up_test(db_name):
    connection = get_connection(alias="default")
    db = connection.get_database(db_name)
    for collection in db.list_collection_names():
        if collection not in ['system.indexes']:
            db.drop_collection(collection)
    disconnect(alias="default")


CUSTOMER_PASSWORD = get_password_hash("customer_password!123")
ADMIN_PASSWORD = get_password_hash("admin_password!123")


def create_admin_user() -> Admin:
    admin_role = Role(name='Admin').save()
    return Admin(name='admin_user', email="admin@gmail.com", password=ADMIN_PASSWORD, role=admin_role).save()


def create_customer_user() -> Customer:
    customer_role = Role(name='Customer').save()
    return Customer(name='customer_user', email="customer@gmail.com", password=CUSTOMER_PASSWORD,
                    role=customer_role).save()


def another_customer(is_active: bool = True):
    if not (customer_role := Role.objects(name='Customer').first()):
        customer_role = Role(name='Customer').save()
    return Customer(name="Another Customer", email="another_customer@gmail.com", password="password",
                    role=customer_role, is_active=is_active)


def another_admin(parent_admin: Optional[Admin] = None, is_active: bool = True):
    if not (admin_role := Role.objects(name='Admin').first()):
        admin_role = Role(name='Admin').save()
    if parent_admin:
        return Admin(name="Test Admin", email="testadmin@gmail.com",
                     parent_admin=parent_admin.id, password="password", role=admin_role, is_active=is_active)
    return Admin(name="Test Admin", email="testadmin@gmail.com", password="password", role=admin_role, is_active=True)