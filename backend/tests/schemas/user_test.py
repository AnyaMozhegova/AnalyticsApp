import pytest

from schemas.user import UserCreate, validate_name, validate_password


@pytest.mark.parametrize("name", ["John", "a" * 20, "Jane Doe"])
def test_validate_name_success(name):
    assert validate_name(name) == name


@pytest.mark.parametrize("name", ["", "a" * 21, " " * 5])
def test_validate_name_failure(name):
    with pytest.raises(ValueError):
        validate_name(name)


@pytest.mark.parametrize("password", ["Password@123", "StrongPass!1"])
def test_validate_password_success(password):
    assert validate_password(password) == password


@pytest.mark.parametrize("password", ["short", "longpasswordwithoutanydigitsorspecialcharacters",
                                      "Valid1!buttoolongpasswordforthiscase", "", " ", "sh ort23748!A", " " * 10])
def test_validate_password_failure(password):
    with pytest.raises(ValueError):
        validate_password(password)


def test_user_create_success():
    user_data = {
        "name": "John Doe",
        "email": "john@example.com"
    }
    user = UserCreate(**user_data)
    assert user.name == user_data["name"]
    assert user.email == user_data["email"]
