import logging
import os

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import FileResponse, JSONResponse, Response

from errors.not_found import NotFoundError
from models.user import User
from services.report import get_current_customer_report, get_current_customer_reports, delete_report, get_report_file, \
    get_report_indicator_values
from services.user import get_current_user

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s:%(asctime)s%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

router = APIRouter(prefix="/report",
                   tags=["reports"],
                   responses={404: {"description": "Report router not found"}})


@router.get("/", status_code=status.HTTP_200_OK)
def get_reports_route(current_user: User = Depends(get_current_user)):
    try:
        return Response(content=get_current_customer_reports(current_user).to_json())
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{report_id}", status_code=status.HTTP_200_OK)
def get_report_route(report_id: int, current_user: User = Depends(get_current_user)):
    try:
        return Response(status_code=status.HTTP_200_OK,
                        content=get_current_customer_report(report_id, current_user).to_json())
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{report_id}", status_code=status.HTTP_200_OK)
def delete_report_route(report_id: int, current_user: User = Depends(get_current_user)):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=delete_report(report_id, current_user))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{report_id}/indicator_values", status_code=status.HTTP_200_OK)
def indicator_values_route(report_id: int, current_user: User = Depends(get_current_user)):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK,
                        content=get_report_indicator_values(report_id, current_user))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{report_id}/file")
async def get_report_file_route(report_id: int, current_user: User = Depends(get_current_user)):
    file_path = get_report_file(report_id, current_user)
    return FileResponse(path=file_path, filename=os.path.basename(file_path), media_type='application/octet-stream')
