from http import HTTPStatus

from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.db.group_methods import get_groups as get_groups_db


router = APIRouter()

@router.get("/api/groups", response_model=list[str], summary="Получение списка групп")
async def get_groups():
    groups = get_groups_db()
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=groups
    )