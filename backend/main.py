#!/usr/bin/env python
# coding: utf-8
import logging
import os

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from mongoengine import connect
from starlette.requests import Request
from starlette.responses import Response

from routers.customer import router as customer_router
from routers.report import router as report_router
from routers.admin import router as admin_router
from services.user import create_token

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s:  %(asctime)s  %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

app = FastAPI(docs_url=None, redoc_url=None)

MONGODB_URL = os.getenv("MONGODB_URL")
connect(host=MONGODB_URL)

app.include_router(report_router)
app.include_router(customer_router)
app.include_router(admin_router)


@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Request-Method"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Request-Headers"] = "content-type"
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response


@app.get("/")
async def root():
    logging.info("Root application started successfully")


@app.post("/login")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    return create_token(form_data.username, form_data.password)


@app.options("/{full_path:path}")
def options_handler(r: Request, full_path: str | None):
    headers = {"Access-Control-Allow-Origin": "*",
               "Access-Control-Allow-Methods": "*",
               "Access-Control-Allow-Headers": "Content-Type"}
    return Response(status_code=200, headers=headers)
