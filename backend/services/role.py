from typing import List, Optional

from errors.not_found import NotFoundError
from models.role import Role
from schemas.role import RoleCreate, RoleUpdate
from services.utils import check_admin_access


def get_roles(user_id: int) -> List[Role]:
    check_admin_access(user_id)
    roles = Role.objects()
    return roles


def get_role(user_id: int, role_id: int) -> Optional[Role]:
    check_admin_access(user_id)
    if role := Role.objects(id=role_id).first():
        return role
    raise NotFoundError(
        f"Could not get role with id = {role_id}. There is no such entity")


def get_role_by_name(user_id: int, role_name: str) -> Optional[Role]:
    check_admin_access(user_id)
    if role := Role.objects(name=role_name).first():
        return role
    raise NotFoundError(
        f"Could not get role with name = {role_name}. There is no such entity")


def update_role(user_id: int, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
    check_admin_access(user_id)
    if role := Role.objects(id=role_id).first():
        for field, value in role_update.dict(exclude_unset=True).items():
            setattr(role, field, value)
        role.save()
        return role
    raise NotFoundError(f"Could not get role with id = {role_id}. There is no such entity")
