from fastapi import APIRouter, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from http import HTTPStatus
from typing import List

from app.core.jwt_handler import decode_access_token
from app.db.student_methods import get_groups_by_faculty, get_student_labs, get_student_labs_by_subject, \
    get_users_by_faculty, get_users_by_group
from app.db.teacher_methods import get_teacher_subjects, get_students_data, create_laboratory, get_laboratories, \
    delete_laboratory, toggle_laboratory_status, get_student_tasks_with_status, get_lab_details, edit_lab, get_laboratoy_with_status
from app.db.user_methods import get_groups_by_user_id, get_username_by_id, is_user_enrolled_in_subject
from app.schemas.teachers import (
    StudentResponse,
    GroupResponse,
    LabResponse,
    LabDetailResponse, CreateLabRequest, UpdateLabRequest, DetailLab
)
from app.schemas.users import FullUserInfo
from app.utils.utils import response_with_json, response_with_error

router = APIRouter(prefix="/api/teachers")

# Получение списка студентов по id факультета
@router.get("/students/{faculty_id}", response_model=List[StudentResponse],
            summary="Получение списка студентов по id факультета")
async def get_students(faculty_id: int):
    students = get_users_by_faculty(faculty_id)
    if isinstance(students, str):
        return response_with_error(
            HTTPStatus.NOT_FOUND,
            students
        )

    serialized_students = [StudentResponse(
        id=student.id,
        full_name=f"{student.last_name} {student.first_name} {student.middle_name}",
        studyGroup=student.studyGroup
    ).model_dump() for student in students]

    return response_with_json(
        HTTPStatus.OK,
        serialized_students
    )


# Получение списка студентов по группе
@router.get("/groups/{group_id}/students", response_model=List[StudentResponse],
            summary="Получение списка студентов по группе")
async def get_students_by_group(group_id: int):
    students = get_users_by_group(group_id)
    if isinstance(students, str):
        return response_with_error(
            HTTPStatus.NOT_FOUND,
            students
        )

    serialized_students: list[StudentResponse] = [StudentResponse(
        id=student.id,
        full_name=f"{student.last_name} {student.first_name} {student.middle_name}",
        studyGroup=student.studyGroup
    ).model_dump() for student in students]

    return response_with_json(
        HTTPStatus.OK,
        serialized_students
    )


# Получение информации о лабораторной работы студента
@router.get("/students/{student_id}/labs/{lab_id}/lab", response_model=LabDetailResponse,
            summary="Получение информации о лабораторной работе студента")
async def get_student_lab_detail(student_id: int, lab_id: int):
    lab = get_student_labs(student_id, lab_id)
    if not lab:
        return response_with_error(
            HTTPStatus.NOT_FOUND,
            "Лабораторная работа не найдена"
        )

    response = LabDetailResponse(
        id=lab.id,
        name=lab.name,
        description=lab.description,
        count_subtasks=lab.count_subtasks,
        status=lab.status,
        solutions=[solution.model_dump() for solution in lab.solutions]
    ).model_dump()

    return response_with_json(
        HTTPStatus.OK,
        response
    )


# Получение лабораторных работ студента
@router.get("/students/{student_id}/subjects/{subject_id}/labs", response_model=list[LabResponse],
            summary="Получение лабораторных работ студента")
async def get_student_tasks(student_id: int, subject_id: int):
    student_username = get_username_by_id(student_id)
    is_enrolled = is_user_enrolled_in_subject(student_username, subject_id)
    if isinstance(is_enrolled, str):
        return response_with_error(
            HTTPStatus.NOT_FOUND,
            is_enrolled
        )

    labs = get_student_labs_by_subject(student_id, subject_id)
    if not labs:
        return response_with_error(
            HTTPStatus.NOT_FOUND,
            "Лабораторные работы не найдены"
        )

    serialized_labs = [LabResponse(
        id=lab.id,
        title=lab.title,
        status=lab.status,
    ).model_dump() for lab in labs]

    return response_with_json(
        HTTPStatus.OK,
        serialized_labs
    )

# Заглушка для получения списка групп факультета
@router.get("/groups/{faculty_id}", response_model=list[GroupResponse], summary="Получение списка групп факультета")
async def get_faculty_groups(faculty_id: int):
    groups = get_groups_by_faculty(faculty_id)
    if isinstance(groups, str):
        return response_with_error(
            HTTPStatus.NOT_FOUND,
            groups
        )

    response: list[GroupResponse] = [
        GroupResponse(
            id=group.id,
            name=group.name,
        ).model_dump() for group in groups
    ]

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=response
    )

# Получение групп преподавателя
@router.get("/groups", response_model=list[GroupResponse], summary="Получение групп преподавателя")
async def get_groups(request: Request):
   
    user_id = request.state.user_id
    groups = get_groups_by_user_id(user_id)

    resposne = [GroupResponse(
        id=group[0],
        name=group[1],
    ).model_dump(
    ) for group in groups]

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=resposne
    )

# Получение дисциплин преподавателя
@router.get("/subjects", response_model=list[LabResponse], summary="Получение дисциплин преподавателя")
async def get_subjects(request: Request):
    user_id = request.state.user_id
    subjects = get_teacher_subjects(user_id)

    response = [subject.model_dump() for subject in subjects]

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=response
    )

# Создание лабораторной работы
@router.post("/lab", response_model=CreateLabRequest)
async def create_lab(lab: CreateLabRequest):
    created_task = create_laboratory(lab.task)
    if created_task is None:
        return response_with_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "Ошибка создания лабораторной работы"
        )
    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content={"id": created_task}
    )

# Список лабораторных работ
@router.get("/labs", response_model=list[LabResponse], summary="Получение списка всех лабораторных работ")
async def get_labs():
   
    labs = get_laboratories()
    response = [lab for lab in labs]

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=response
    )

# Список опубликованных лабораторных работ
@router.get("/labs/status/published", response_model=list[LabResponse], summary="Получение списка опубликованных лабораторных работ")
async def get_labs_published():
   
    labs = get_laboratoy_with_status("published")
    response = [lab for lab in labs]

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=response
    )

# Список неопубликованных лабораторных работ
@router.get("/labs/status/unpublished", response_model=list[LabResponse], summary="Получение списка не опубликованных лабораторных работ")
async def get_labs_unpublished():
   
    labs = get_laboratoy_with_status("unpublished")
    response = [lab for lab in labs]

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=response
    )

# Удаление лабораторной работы
@router.delete("/labs/{lab_id}", summary="Удаление лабораторной работы")
async def delete_lab(lab_id: int):
    result = delete_laboratory(lab_id)
    if not result:
        return response_with_error(
            HTTPStatus.NOT_FOUND,
            "Лабораторная работа не найдена"
        )

    return JSONResponse(
        status_code=HTTPStatus.NO_CONTENT,
        content={"message": "Лабораторная работа успешно удалена"}
    )

# Изменение статуса лабораторной работы
@router.put("/labs/{lab_id}/toggle", summary="Опубликование лабораторной работы")
async def toggle_status_lab(lab_id: int):
    result = toggle_laboratory_status(lab_id)
    if not result:
        return response_with_error(
            HTTPStatus.NOT_FOUND,
            "Лабораторная работа не найдена"
        )
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={"message": "Статус лабораторной работы успешно изменен"}
    )

# Редактирование лабораторной работы
@router.put("/labs/{lab_id}", response_model=UpdateLabRequest, summary="Редактирование лабораторной работы")
async def edit_lab_endpoint(lab_id: int, lab: UpdateLabRequest):
   
    task_to_update = edit_lab(lab_id, lab)
    if not task_to_update:
        return response_with_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "Ошибка редактирования лабораторной работы"
        )
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={"id": lab_id}
    )

# Информация о пользователе
@router.get("/students/{student_id}/info", summary="Информация о пользователе", response_model=FullUserInfo)
async def get_students_info(student_id: int):
    data = get_students_data(student_id)
    if isinstance(data, str):
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"error": data}
        )

    response = data.model_dump()

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=response
    )

# Получение всех лаб студента
@router.get("/students/{student_id}/labs", response_model=list[LabResponse], summary="Получение всех лаб студента")
async def get_student_labs(student_id: int):
    user_labs = get_student_tasks_with_status(student_id)

    serialized_labs = [lab for lab in user_labs]

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=serialized_labs
    )

# Получение деталей лабораторной работы
@router.get("/labs/{lab_id}", response_model=DetailLab, summary="Получение деталей неопубликованной лабораторной работы")
async def get_unpublished_task_details(lab_id: int):
    labs = get_lab_details(lab_id)
    if not labs:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"error": "Лабораторная работа не найдена"}
        )

    response = DetailLab(
        id=labs.get("id"),
        name=labs.get("name"),
        description=labs.get("description"),
        teacher_formula=labs.get("teacher_formula"),
        input_variables=labs.get("input_variables"),
        subject_id=labs.get("subject_id"),
        test_cases=[{"id": case.get("id"), "inp": case["input"], "out": case["output"]} for case in labs.get("test_cases", [])]
).model_dump()

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=response
    )