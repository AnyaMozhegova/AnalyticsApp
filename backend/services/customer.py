from typing import List, Optional
from fastapi import Depends
from starlette.responses import JSONResponse

from errors.bad_request import BadRequestError
from errors.not_found import NotFoundError

from models.customer import Customer
from models.role import Role
from models.user import User
from models.report import Report

from schemas.customer import CustomerCreate, CustomerUpdate

from services.user import create_token, get_current_user, get_password_hash, get_user_by_email


def create_customer(customer_body: CustomerCreate) -> JSONResponse:
    if get_user_by_email(customer_body.email):
        raise BadRequestError(f"Could not create customer with body = {customer_body}. User with such email already "
                              f"exists. Try to sign in")
    if customer_body.password != customer_body.password_confirm:
        raise BadRequestError(
            f"Could not create customer with body = {customer_body}. Password and confirm password do not match.")
    hashed_password = get_password_hash(customer_body.password)
    customer_role = Role.objects(name='Customer').first()
    customer = Customer(name=customer_body.name, email=customer_body.email, role=customer_role, is_active=True,
                        password=hashed_password)
    customer.save()
    response = create_token(customer_body.email, customer_body.password)
    response.status_code = 201
    return response


def delete_customer(current_user: User = Depends(get_current_user)) -> None:
    if not current_user or not (customer := Customer.objects(id=current_user.id, is_active=True).first()):
        raise NotFoundError(f"Could not delete customer {current_user}. Customer does not exist.")
    customer.is_active = False
    customer.save()


def get_customer(customer_id: int) -> Optional[Customer]:
    if not (customer := Customer.objects(id=customer_id, is_active=True).first()):
        raise NotFoundError(f"Could not get customer with id = {customer_id}. Customer does not exist.")
    return customer


def get_current_customer(current_user: User = Depends(get_current_user)) -> Optional[Customer]:
    if not current_user or not (customer := Customer.objects(id=current_user.id, is_active=True).first()):
        raise NotFoundError(f"Could not get customer {current_user}. Customer does not exist.")
    return customer


def get_customers() -> List[Customer]:
    return Customer.objects(is_active=True)


def update_customer(customer_update: CustomerUpdate, current_user: User = Depends(get_current_user)) -> None:
    if not current_user or not (customer_to_update := Customer.objects(id=current_user.id, is_active=True).first()):
        raise NotFoundError(f"Could not update customer {current_user}. Customer does not exist.")
    if customer_update.name:
        customer_to_update.name = customer_update.name
    if customer_update.password:
        if customer_update.password != customer_update.password_confirm:
            raise BadRequestError(
                f"Could not update customer with id = {current_user.id}. Password and confirm password do not match.")
        customer_to_update.password = get_password_hash(customer_update.password)
    customer_to_update.save()
