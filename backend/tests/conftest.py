import pytest
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect
from main import app
from models.user import User
from models.role import Role


@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def mongo_db():
    db_name = "test_db"
    connect(db_name, host="mongomock://localhost", alias="default")
    yield db_name
    disconnect(alias="default")


@pytest.fixture(scope="function")
def create_test_customer(mongo_db):
    def _create_test_user(username, email, password, role):
        user = User(name=username, email=email, password=password, role=Role.objects(id=role).first())
        user.save()
        return user

    return _create_test_user


@pytest.fixture(scope="function")
def clean_up():
    yield
    User.objects.delete()
