from typing import Union

from fastapi import APIRouter, Header, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from http import HTTPStatus

from app.core.check_auth import check_auth
from app.core.files.files import check_type
from app.db.subject_methods import get_subject_id_by_task
from app.db.task_methods import add_solution, get_latest_solution, get_task_data, get_user_solutions_by_task
from app.db.user_methods import is_user_enrolled_in_subject
from app.schemas.files import ResponseUpload
from app.schemas.others import Error
from app.schemas.task import TaskInfo, SolutionInfo
from app.schemas.test import ResponseTest
from app.testing_pyfiles.test import check_file
from app.utils.utils import response_with_json

router = APIRouter()


# Загрузка решения задачи по task_id
@router.post("/upload/{task_id}", response_model=ResponseUpload, summary="Загрузка кода для лабораторной работы")
async def upload_solution(task_id: int, authorization: str = Header(...), file: UploadFile = File(...)):
    check_data = check_auth(authorization)
    if isinstance(check_data, JSONResponse):
        return check_data

    # Проверка типа файла
    check_file = check_type(file)
    if not check_file[0]:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"error": check_file[1]}
        )

    file_content = await file.read()

    # Добавление решения в БД
    res_add_solution = add_solution(
        code=file_content.decode('utf-8'),
        user_id=check_data['user_id'],
        task_id=task_id,
    )

    # Если решение не добавлено
    if isinstance(res_add_solution, str):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"error": res_add_solution}
        )

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=ResponseUpload(
            task_id=task_id,
        ).model_dump()
    )


# Тестирование файла
@router.post("/test/{task_id}", response_model=ResponseTest, summary="Тестирование лабораторной работы")
async def test_solution(task_id: int, authorization: str = Header(...)):
    check_data = check_auth(authorization)
    if isinstance(check_data, JSONResponse):
        return check_data

    # Проверка, что пользователь принадлежит предмету, к которому относится задача
    subject_id = get_subject_id_by_task(task_id)
    if not subject_id:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"error": "Task not found."}
        )

    user_enrolled = is_user_enrolled_in_subject(check_data['username'], subject_id)
    if not user_enrolled:
        return JSONResponse(
            status_code=HTTPStatus.FORBIDDEN,
            content={"error": "User is not enrolled in the subject."}
        )

    # Получение данных задачи
    task_data = get_task_data(task_id)
    if not task_data:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"error": "Task data not found."}
        )

    # Получение последнего решения пользователя
    latest_solution = get_latest_solution(check_data['user_id'], task_id)
    if not latest_solution:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"error": "Solution not found."}
        )

    # Выполнение тестирования
    res_check = await check_file(
        task_id,
        task_data['teacher_formula'],
        task_data['input_variables'],
        latest_solution.code,
        latest_solution.id
    )

    response = ResponseTest(
        status=res_check.execution_status,
        formulas_output=res_check.formulas_output,
        code_output=res_check.code_output,
        execution_time=res_check.execution_time,
        code_length=res_check.code_length,
    ).model_dump()

    if res_check.execution_status == "Failed":
        return response_with_json(
            HTTPStatus.BAD_REQUEST,
            response
        )

    return response_with_json(
        HTTPStatus.OK,
        response
    )


# Получение информации о задаче по task_id и информация о том, сдал ли пользователь
# хотя бы одно правильное решение
@router.get("/task/{task_id}", response_model=Union[TaskInfo, Error],
            summary="Получение информации о лабораторной работе и всех ее загруженных решениях")
async def get_task_info(task_id: int, authorization: str = Header(...)):
    check_data = check_auth(authorization)
    if isinstance(check_data, JSONResponse):
        return check_data

    # Получение данных задачи
    task_data = get_task_data(task_id)
    if not task_data:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"error": "Task not found."}
        )

    # Получение решений пользователя для задачи
    user_solutions = get_user_solutions_by_task(check_data['user_id'], task_id)
    # if not user_solutions:
    #     return JSONResponse(
    #         status_code=HTTPStatus.NOT_FOUND,
    #         content=Error(message="No solutions found for this task.").model_dump()
    #     )

    # Проверка, есть ли хотя бы одно успешное решение
    passed_solutions = [sol for sol in user_solutions if sol.status == "Success"]
    status = "Success" if passed_solutions else "Failed"

    # Формирование ответа
    solutions_info = [SolutionInfo(code=sol.code, status=sol.status or "unknown").model_dump() for sol in
                      user_solutions]
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=TaskInfo(
            id=task_data['id'],
            name=task_data['name'],
            description=task_data['description'],
            count_subtasks=1,
            status=status,
            solutions=solutions_info,
        ).model_dump()
    )
