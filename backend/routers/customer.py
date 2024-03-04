import logging
from starlette import status
from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer

from errors.bad_request import BadRequestError
from errors.not_found import NotFoundError
from models.user import User
from passlib.context import CryptContext
from schemas.customer import CustomerCreate, CustomerUpdate
from services.customer import create_customer, delete_customer, get_current_customer, update_customer, \
    delete_customer_by_admin, get_customers
from services.report import create_report
from services.user import get_current_user

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s:%(asctime)s%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

router = APIRouter(prefix="/customer",
                   tags=["customers"],
                   responses={404: {"description": "Customer router not found"}})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
def sign_up_route(customer_body: CustomerCreate):
    try:
        return create_customer(customer_body)
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_current_customer_route(current_user: User = Depends(get_current_user)):
    try:
        delete_customer(current_user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/me", status_code=status.HTTP_200_OK)
def get_current_customer_route(current_user: User = Depends(get_current_user)):
    try:
        return JSONResponse(content=get_current_customer(current_user).to_json())
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{customer_id}", status_code=status.HTTP_200_OK)
def delete_customer_by_admin_route(customer_id: int, current_user: User = Depends(get_current_user)):
    try:
        delete_customer_by_admin(customer_id, current_user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", status_code=status.HTTP_200_OK)
def get_customers_route(current_user: User = Depends(get_current_user)):
    try:
        return JSONResponse(content=get_customers(current_user).to_json())  # type: ignore
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/me", status_code=status.HTTP_200_OK)
def update_customer_route(customer_body: CustomerUpdate, current_user: User = Depends(get_current_user)):
    try:
        return JSONResponse(content=update_customer(customer_body, current_user))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/upload_report", status_code=status.HTTP_200_OK)
async def upload_report_route(report: UploadFile, current_user: User = Depends(get_current_user)):
    try:
        return await create_report(report, current_user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
