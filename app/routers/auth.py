from datetime import timedelta

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from http import HTTPStatus

from app.config.config import init_config
from app.core.jwt_handler import create_access_token
from app.db.user_methods import add_user, validate_user
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse

router = APIRouter()
cfg = init_config()['jwt']


@router.post("/login", response_model=LoginResponse, summary="Авторизация пользователя")
async def login(request: LoginRequest):
    user_data = validate_user(
        username=request.username,
        password=request.password
    )
    # if already exists in db
    if not user_data:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"error": "User already exists"}
        )

    # generate jwt token & more
    user_token = create_access_token(user_data, timedelta(seconds=cfg['expires_in']))
    login_response = LoginResponse(access_token=user_token)
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=login_response.model_dump()
    )


@router.post("/register", response_model=RegisterResponse, summary="Регистрация пользователя")
async def register(request: RegisterRequest):
    user_data = validate_user(
        username=request.username,
        password=request.password
    )
    # if not exists in db
    if user_data:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"error": "User already exists"}
        )

    # add user to db
    res_data = add_user(request)
    if isinstance(res_data, str):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"error": res_data}
        )

    jwt_data = {
        "user_id": res_data.get('user_id'),
        "username": res_data.get('username'),
        "roleType": res_data.get('roleType'),
        "studyGroup": res_data.get('studyGroup')
    }

    # generate jwt token & more
    user_token = create_access_token(jwt_data, timedelta(seconds=cfg['expires_in']))
    register_response = RegisterResponse(
        access_token=user_token,
        role=res_data.get('roleType', 'unknown'),
    )
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=register_response.model_dump()
    )