import pytest
from pydantic import ValidationError

from schemas.customer import CustomerCreate


def test_customer_create_success():
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "Password!123",
        "password_confirm": "Password!123"
    }
    user = CustomerCreate(**user_data)
    assert user.name == user_data["name"]
    assert user.email == user_data["email"]
    assert user.password == user_data["password"]


def test_customer_create_password_mismatch():
    user_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "Password@123",
        "password_confirm": "DifferentPassword@123"
    }
    with pytest.raises(ValidationError):
        CustomerCreate(**user_data)
