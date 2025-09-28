from http import HTTPStatus

from starlette.responses import JSONResponse


def response_with_error(code: HTTPStatus, msg: str) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        content={"Error": msg}
    )

def response_with_json(code: HTTPStatus, data: any) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        content=data
    )