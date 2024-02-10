import pytest
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect, get_connection
from main import app
from models.user import User
from models.role import Role


@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client


import mongomock
import pytest
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
    admin_role = Role(name='admin').save()
    user = User(name='admin_user', email="admin@gmail.com", password="admin_password!123",
                role=admin_role)
    user.save()
    return user


def create_customer_user() -> User:
    customer_role = Role(name='customer').save()
    user = User(name='customer_user', email="customer@gmail.com", password="customer_password!123",
                role=customer_role)
    user.save()
    return user
