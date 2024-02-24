import pytest
from fastapi.testclient import TestClient
from main import app
from models.admin import Admin
from models.role import Role
from models.user import User
from mongoengine import get_connection


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


def create_admin_user() -> User:
    admin_role = Role(name='Admin').save()
    user = Admin(name='admin_user', email="admin@gmail.com", password="admin_password!123",
                 role=admin_role)
    user.save()
    return user


def create_customer_user() -> User:
    customer_role = Role(name='Customer').save()
    user = User(name='customer_user', email="customer@gmail.com", password="customer_password!123",
                role=customer_role)
    user.save()
    return user
