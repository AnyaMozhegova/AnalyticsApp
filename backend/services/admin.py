import json
from typing import List, Optional

from errors.bad_request import BadRequestError
from errors.forbidden import ForbiddenError
from errors.not_found import NotFoundError
from fastapi import Depends
from models.admin import Admin
from models.role import Role
from models.user import User
from schemas.admin import AdminCreate, AdminDelete, AdminUpdate
from services.user import create_token, get_current_user, get_password_hash, get_user_by_email
from services.utils import check_admin_access, generate_password
from starlette.responses import JSONResponse


def validate_parent(current_user: User, parent_admin_id: int, error_message: str):
    if not (parent_admin := Admin.objects(id=parent_admin_id, is_active=True).first()):
        raise NotFoundError(
            f"Could not {error_message} admin with parent admin id = {parent_admin_id}, Admin does not exists.")
    if current_user.id != parent_admin.id:
        raise ForbiddenError(
            f"Could not {error_message} admin with parent admin id = {parent_admin.id}. Current user does not match.")
    check_admin_access(current_user.id)


def create_admin(admin_body: AdminCreate, current_user: User = Depends(get_current_user)) -> JSONResponse:
    validate_parent(current_user, admin_body.parent_admin, "create")
    if get_user_by_email(admin_body.email):
        raise BadRequestError(f"Could not create admin with body = {admin_body}. User with such email already "
                              f"exists. Try to sign in")
    admin_password = generate_password()
    hashed_password = get_password_hash(admin_password)
    admin_role = Role.objects(name='admin').first()
    user = Admin(name=admin_body.name, email=admin_body.email, role=admin_role, parent_admin=admin_body.parent_admin,
                 password=hashed_password)
    user.save()
    response = create_token(admin_body.email, admin_password)
    content = json.loads(response.body)
    content['admin_password'] = admin_password
    return JSONResponse(content=content, status_code=response.status_code)


def delete_admin(admin_delete: AdminDelete, current_user: User = Depends(get_current_user)) -> None:
    if not (deleted_admin := Admin.objects(id=admin_delete.admin_to_delete, is_active=True).first()):
        raise NotFoundError(f"Could not delete admin with id = {admin_delete.admin_to_delete}. Admin does not exist.")
    if deleted_admin.parent_admin:
        validate_parent(current_user, deleted_admin.parent_admin.id, "delete")
        deleted_admin.is_active = False
        deleted_admin.save()
    else:
        raise ForbiddenError(f"Could not delete admin with id = {admin_delete.admin_to_delete}. Admin is a root admin")


def get_admin(admin_id: int) -> Optional[Admin]:
    if not (admin := Admin.objects(id=admin_id, is_active=True).first()):
        raise NotFoundError(f"Could not get admin with id = {admin_id}. Admin does not exist.")
    return admin


def get_admin_children_by_current_user(current_user: User = Depends(get_current_user)) -> Optional[List[Admin]]:
    validate_parent(current_user, current_user.id, "get")
    return Admin.objects(parent_admin=current_user.id, is_active=True)


def get_admin_children(admin: Admin) -> List[Admin]:
    return Admin.objects(is_active=True, parent_admin=admin)


def get_admins() -> List[Admin]:
    return Admin.objects(is_active=True)


def update_admin(admin_update: AdminUpdate, current_user: User = Depends(get_current_user)) -> None:
    check_admin_access(current_user.id)
    admin_to_update = Admin.objects(id=current_user.id, is_active=True).first()

    if admin_update.name:
        admin_to_update.name = admin_update.name
    if admin_update.password:
        if admin_update.password != admin_update.password_confirm:
            raise BadRequestError(
                f"Could not update admin with id = {current_user.id}. Password and confirm password do not match.")
        admin_to_update.password = get_password_hash(admin_update.password)
    admin_to_update.save()
