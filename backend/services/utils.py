from typing import List, Optional

from models.role import Role
from models.user import User

from errors.forbidden import ForbiddenError
from errors.not_found import NotFoundError

from models.report_column import ReportColumn


def models_to_dict(objs: list):
    return [obj.to_dict() for obj in objs]


def check_admin_access(user_id: int) -> Optional[bool]:
    if user := User.objects(id=user_id, is_active=True).first():
        if (role := Role.objects(id=user.role.id).first()) and role.name.lower() == 'admin':
            return True
        raise NotFoundError("User is not found")
    raise ForbiddenError("User doesn't have admin access")


def check_customer_access(user_id: int) -> Optional[bool]:
    if user := User.objects(id=user_id, is_active=True).first():
        if (role := Role.objects(id=user.role.id).first()) and role.name.lower() == 'customer':
            return True
        raise NotFoundError("User is not found")
    raise ForbiddenError("User doesn't have customer access")


def filter_column_data(column: ReportColumn) -> Optional[List[float]]:
    filtered_data = [value for value in column.column_data if value is not None]
    return filtered_data if len(filtered_data) > 0 else None
