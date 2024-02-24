import random
import re
from re import Match
from typing import List, Optional

from models.role import Role
from models.user import User

from errors.forbidden import ForbiddenError
from errors.not_found import NotFoundError

from models.report_column import ReportColumn

from models.admin import Admin


def models_to_dict(objs: list):
    return [obj.to_dict() for obj in objs]


def check_admin_access(admin_id: int) -> Optional[bool]:
    if admin := Admin.objects(id=admin_id, is_active=True).first():
        if (role := Role.objects(id=admin.role.id).first()) and role.name.lower() == 'admin':
            return True
        raise NotFoundError(f"Admin with id = {admin_id} is not found")
    raise ForbiddenError(f"Admin with id = {admin_id} doesn't have admin access")


def check_customer_access(user_id: int) -> Optional[bool]:
    if user := User.objects(id=user_id, is_active=True).first():
        if (role := Role.objects(id=user.role.id).first()) and role.name.lower() == 'customer':
            return True
        raise NotFoundError("User is not found")
    raise ForbiddenError("User doesn't have customer access")


def filter_column_data(column: ReportColumn) -> Optional[List[float]]:
    filtered_data = [value for value in column.column_data if value is not None]
    return filtered_data if len(filtered_data) > 0 else None


def password_match_patterns(password: str) -> Optional[Match[str]]:
    pattern = (
        r'^'
        r'(?=.*[a-z])'
        r'(?=.*[A-Z])'
        r'(?=.*\d)'
        r'(?=.*[@$!%*?&])'
        r'[A-Za-z\d@$!%*?&]+'
        r'$'
    )
    return re.match(pattern, password)


def generate_password(length=12):
    lowercase_letters = 'abcdefghijklmnopqrstuvwxyz'
    uppercase_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    digits = '0123456789'
    special_characters = '@$!%*?&'

    password = [
        random.choice(lowercase_letters),
        random.choice(uppercase_letters),
        random.choice(digits),
        random.choice(special_characters)
    ]

    all_characters = lowercase_letters + uppercase_letters + digits + special_characters
    password += [random.choice(all_characters) for _ in range(length - 4)]

    random.shuffle(password)
    password_str = ''.join(password)

    if password_match_patterns(password_str):
        return password_str
    else:
        return generate_password(length)
