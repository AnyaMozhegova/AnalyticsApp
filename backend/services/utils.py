from typing import Optional

from models.role import Role
from models.user import User

from errors.forbidden import ForbiddenError
from errors.not_found import NotFoundError


def models_to_dict(objs: list):
    return [obj.to_dict() for obj in objs]


def check_admin_access(user_id: int) -> Optional[bool]:
    if user := User.objects(id=user_id).first():
        if (role := Role.objects(id=user.role.id).first()) and role.name.lower() == 'admin':
            return True
        raise NotFoundError("User is not found")
    raise ForbiddenError("User doesn't have admin access")


def check_customer_access(user_id: int) -> Optional[bool]:
    if user := User.objects(id=user_id).first():
        if (role := Role.objects(id=user.role.id).first()) and role.name.lower() == 'customer':
            return True
        raise NotFoundError("User is not found")
    raise ForbiddenError("User doesn't have customer access")
