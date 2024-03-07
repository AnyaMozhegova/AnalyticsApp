import logging

from errors.bad_request import BadRequestError
from errors.not_found import NotFoundError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models.user import User
from passlib.context import CryptContext
from services.user import get_current_user
from starlette import status
from starlette.responses import JSONResponse, Response

from errors.forbidden import ForbiddenError
from schemas.admin import AdminCreate, AdminUpdate
from services.admin import create_admin, delete_admin, \
    get_admin_children_by_current_user, get_admins, get_current_admin, update_admin

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s:%(asctime)s%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

router = APIRouter(prefix="/admin",
                   tags=["admins"],
                   responses={404: {"description": "Admin router not found"}})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_admin_route(admin_body: AdminCreate, current_user: User = Depends(get_current_user)):
    try:
        return create_admin(admin_body, current_user)
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{admin_to_delete_id}", status_code=status.HTTP_200_OK)
def delete_child_admin_route(admin_to_delete_id: int, current_user: User = Depends(get_current_user)):
    try:
        delete_admin(admin_to_delete_id, current_user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/children", status_code=status.HTTP_200_OK)
def get_current_admin_children_route(current_user: User = Depends(get_current_user)):
    try:
        return JSONResponse(content=get_admin_children_by_current_user(current_user).to_json())  # type: ignore
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/me", status_code=status.HTTP_200_OK)
def get_current_admin_route(current_user: User = Depends(get_current_user)):
    try:
        return Response(content=get_current_admin(current_user).to_json())
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", status_code=status.HTTP_200_OK)
def get_admins_route(current_user: User = Depends(get_current_user)):
    try:
        return Response(content=get_admins(current_user).to_json())
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/me", status_code=status.HTTP_200_OK)
def update_admin_route(admin_body: AdminUpdate, current_user: User = Depends(get_current_user)):
    try:
        return JSONResponse(content=update_admin(admin_body, current_user))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
