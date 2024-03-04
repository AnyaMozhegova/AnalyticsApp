import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from errors.not_found import NotFoundError
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyCookie, OAuth2PasswordBearer
from models.user import User
from passlib.context import CryptContext
from schemas.user import TokenData
from starlette import status
from starlette.responses import JSONResponse

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s:%(asctime)s%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
from dotenv import load_dotenv

dotenv_path = '.env'
load_dotenv(dotenv_path=dotenv_path)

cookie_sec = APIKeyCookie(name="session")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
BACKEND_DOMAIN = os.getenv('BACKEND_DOMAIN')
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv('ACCESS_TOKEN_EXPIRE_SECONDS'))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_by_email(email: str) -> Optional[User]:
    return User.objects(email=email, is_active=True).first()


def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user_by_email(username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=int(ACCESS_TOKEN_EXPIRE_SECONDS))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(session: str = Depends(cookie_sec)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(session, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except Exception:
        raise credentials_exception
    user = get_user_by_email(token_data.username)
    if user is None:
        raise credentials_exception
    return user


def check_user_access(user_id: int, current_user: User) -> None:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to access this resource")


def create_token(email: str, password: str) -> JSONResponse:
    user = authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    response = JSONResponse(content={"id": user.id, "role": user.role.name.lower()})
    response.set_cookie(key="session", value=access_token, expires=ACCESS_TOKEN_EXPIRE_SECONDS, samesite="none",
                        secure=True, httponly=True, domain=BACKEND_DOMAIN)
    return response


def get_user(user_id: int, current_user: User = Depends(get_current_user)) -> Optional[dict]:
    check_user_access(user_id, current_user)
    if user := User.objects(id=user_id, is_active=True).first():
        return user.to_dict()
    else:
        raise NotFoundError(f"Could not get user with id = {user_id}. There is no such entity")


def me(current_user=Depends(get_current_user)) -> dict[str, int]:
    return {"id": current_user.id}
