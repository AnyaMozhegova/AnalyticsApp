import pytest
from pydantic import ValidationError

from backend.schemas.role import RoleCreate, validate_name


@pytest.mark.parametrize("name", ["Author", "Super admin", "a" * 10])
def test_validate_name_success(name):
    assert validate_name(name) == name


@pytest.mark.parametrize("name", ["", "a" * 21, " " * 5])
def test_validate_name_failure(name):
    with pytest.raises(ValueError):
        validate_name(name)


def test_role_create_success():
    role_data = {
        "name": "Admin",
    }
    role = RoleCreate(**role_data)
    assert role.name == role_data["name"]


def test_role_create_password_mismatch():
    role_data = {
        "name": " " * 5
    }
    with pytest.raises(ValidationError):
        RoleCreate(**role_data)
