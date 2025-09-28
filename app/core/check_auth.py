from http import HTTPStatus
from typing import Union

from fastapi import Header, HTTPException
from starlette.responses import JSONResponse

from app.core.jwt_handler import decode_access_token


def check_auth(authorization: str = Header(...)) -> Union[JSONResponse, dict]:
    """
    Устаревший метод авторизации. Сейчас лучше делать через /middleware/auth.py и развивать его
    """
    if not authorization.startswith("Bearer "):
        return JSONResponse(status_code=HTTPStatus.UNAUTHORIZED, content={"error": "Invalid token format"})

    token = authorization[len("Bearer "):]
    data = decode_access_token(token)
    if isinstance(data, str):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"error": data}
        )

    return data