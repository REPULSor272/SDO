from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from http import HTTPStatus

from app.core.check_auth import check_auth

from app.db.student_methods import get_student_tasks_with_status
from app.db.task_methods import get_tasks_by_subject, get_user_solutions_by_task
from app.db.user_methods import get_user_subjects, is_user_enrolled_in_subject
from app.schemas.others import Error
from app.schemas.subject import SubjectInfo
from app.schemas.task import Task

router = APIRouter()


# return user subjects [[1, "Python", 5], [2, "C++", 7]] or "Subjects not found" | [id, name, grade]
@router.get("/subjects", response_model=list[SubjectInfo], summary="Получение всех предметов пользователя")
async def get_subjects(authorization: str = Header(...)) -> JSONResponse:
    check_data = check_auth(authorization)
    if isinstance(check_data, JSONResponse):
        return check_data

    user_subjects = get_user_subjects(check_data['username'])

    serialized_subjects = [subject.model_dump() for subject in user_subjects]

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=serialized_subjects
    )


# return tasks of subject by subject_id
@router.get("/tasks/{subject_id}", response_model=list[Task], summary="Получение лабораторных работ предмета")
async def get_tasks(subject_id: str, authorization: str = Header(...)) -> JSONResponse:
    check_data = check_auth(authorization)
    if isinstance(check_data, JSONResponse):
        return check_data
    user_subjects = is_user_enrolled_in_subject(check_data['username'], subject_id)

    # Если пользователь не прикреплен к дисциплине или дисциплина не найдена
    if isinstance(user_subjects, str):
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"error": user_subjects}
        )

    # Получение решений пользователя для задачи
    user_solutions = get_tasks_by_subject(subject_id)
    if not user_solutions:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content=Error(message="No solutions found for this task.").model_dump()
        )

    # Проверка, есть ли хотя бы одно успешное решение
    subject_tasks = get_tasks_by_subject(subject_id)

    serialized_tasks = []
    print(subject_tasks)
    for task in subject_tasks:
        print(task)
        user_solutions = get_user_solutions_by_task(check_data['user_id'], task.id)

        passed_solutions = [sol for sol in user_solutions if sol.status == "Success"]
        status = "Success" if passed_solutions else "Failed"
        task.status = status
        serialized_tasks.append(task.model_dump())

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=serialized_tasks
    )

@router.get("/labs")
async def get_user_labs(authorization: str = Header(...)) -> JSONResponse:
    check_data = check_auth(authorization)
    if isinstance(check_data, JSONResponse):
        return check_data

    user_labs = get_student_tasks_with_status(check_data['user_id'])

    serialized_labs = [lab for lab in user_labs]

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=serialized_labs
    )