from typing import Union

from app.db.db import Group, GroupSubject, Session, Subject, TestCase, User
from app.db.task_methods import is_task_completed
from app.schemas.subject import SubjectInfo
from app.db.db import Task
from app.schemas.teachers import TaskWithTestCasesSchema, UpdateLabRequest
from app.schemas.users import FullUserInfo


def get_teacher_subjects(user_id: int) -> list[SubjectInfo]:
    """
    Получает список дисциплин, связанных с преподавателем по его ID.

    :param user_id: ID преподавателя
    :return: Список объектов SubjectInfo
    """
    with Session() as session:
        # Получаем id группы преподавателя

        group_id = session.query(User.studyGroup).filter(User.id == user_id).first()
        if not group_id:
            return []

        # Получаем id факультета
        faculty_id = session.query(Group.faculty).filter(Group.id == group_id[0]).first()

        # Получаем группы, связанные с факультетом
        teacher_groups = session.query(Group).filter(Group.faculty == faculty_id[0]).all()

        # Получаем факультеты, связанные с этими группами
        faculty_ids = {group.faculty for group in teacher_groups if group.faculty}

        if not faculty_ids:
            return []

        # Получаем все группы, связанные с этими факультетами
        faculty_groups = session.query(Group).filter(Group.faculty.in_(faculty_ids)).all()

        if not faculty_groups:
            return []

        # Получаем дисциплины, связанные с этими группами
        group_ids = [group.id for group in faculty_groups]
        subjects = session.query(Subject).join(GroupSubject).filter(GroupSubject.group_id.in_(group_ids)).all()

        # Формируем список объектов SubjectInfo
        return [SubjectInfo(id=subject.id, name=subject.name, grade=None) for subject in subjects]


def get_students_data(student_id: int) -> Union[FullUserInfo, str]:
    """
    Получает информацию о студенте по его ID.

    :param student_id: ID студента
    :return: Объект FullUserInfo с информацией о студенте или сообщение об ошибке
    """
    with Session() as session:
        try:
            # Получаем пользователя по ID
            user = session.query(User).filter_by(id=student_id).first()

            if not user:
                return f"Студент с ID {student_id} не найден"

            # Проверяем, имеет ли пользователь роль студента
            if user.roleType != 'student':
                return f"Пользователь с ID {student_id} не является студентом"

            # Получаем информацию о группе и факультете
            study_group_name = user.group_rel.name if user.group_rel else "Не указано"
            faculty_name = (
                user.group_rel.faculty_rel.name
                if user.group_rel and user.group_rel.faculty_rel
                else "Не указано"
            )

            # Формируем объект с информацией о студенте
            user_info = FullUserInfo(
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                study_group=study_group_name,
                faculty=faculty_name,
                form_education=user.form_education
            )

            return user_info

        except Exception as e:
            print(f"Error retrieving student info: {e}")
            return f"Ошибка при получении информации о студенте: {str(e)}"


def create_laboratory(task: TaskWithTestCasesSchema):
    """
    Создаёт лабораторную работу и связанные с ней тест-кейсы.

    :param task: TaskWithTestCasesSchema с данными задачи и тест-кейсов
    :return: id созданной лабораторной работы или None при ошибке
    """
    with Session() as session:
        try:
            lab = Task(
                name=task.name,
                description=task.description,
                Subject_id=task.subject_id,
                teacher_formula=task.teacher_formula,
                input_variables=task.input_variables,
                status='unpublished'
            )
            session.add(lab)
            session.commit()

            # Добавляем тест-кейсы
            for test_case in task.test_cases:
                test = TestCase(
                    inp=test_case.inp,
                    out=test_case.out,
                    Task_id=lab.id
                )
                session.add(test)
            session.commit()
            return lab.id
        except Exception as e:
            session.rollback()
            print(f"Ошибка при создании лабораторной: {e}")
            return None


def get_laboratories():
    """
    Получает список всех лабораторных работ с базовой информацией.

    :return: Список словарей с id, именем, именем предмета и статусом лабораторной
    """
    with Session() as session:
        try:
            labs = session.query(Task).all()
            response = [
                {
                    "id": lab.id,
                    "name": lab.name,
                    "subject": lab.subject.name if lab.subject else "Не указано",
                    "status": lab.status
                }
                for lab in labs
            ]
            return response
        except Exception as e:
            print(f"Ошибка при получении лабораторных работ: {e}")
            return []

def get_laboratoy_with_status(target_status: str):
    """
    Получает список всех лабораторных работ по указанному статусу с базовой информацией.

    :return: Список словарей с id, именем, именем предмета и статусом лабораторной
    """
    with Session() as session:
        try:
            labs = session.query(Task).filter_by(status=target_status).all()
            response = [
                {
                    "id": lab.id,
                    "name": lab.name,
                    "subject": lab.subject.name if lab.subject else "Не указано",
                    "status": lab.status
                }
                for lab in labs
            ]
            return response
        except Exception as e:
            print(f"Ошибка при получении лабораторных работ: {e}")
            return []


def delete_laboratory(lab_id: int) -> bool:
    """
    Удаляет лабораторную работу и связанные с ней тест-кейсы.

    :param lab_id: ID лабораторной работы
    :return: True, если удаление прошло успешно, иначе False
    """
    with Session() as session:
        try:
            lab = session.query(Task).filter_by(id=lab_id).first()
            if not lab:
                return False
            session.query(TestCase).filter_by(Task_id=lab_id).delete()
            session.delete(lab)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Ошибка при удалении лабораторной: {e}")
            return False

def toggle_laboratory_status(lab_id: int) -> bool:
    """
    Переключает статус лабораторной работы между 'published' и 'unpublished'.

    :param lab_id: ID лабораторной работы
    :return: True, если изменение прошло успешно, иначе False
    """
    with Session() as session:
        try:
            lab = session.query(Task).filter_by(id=lab_id).first()
            if not lab:
                return False
            if lab.status == 'published':
                lab.status = 'unpublished'
            else:
                lab.status = 'published'
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Ошибка при изменении статуса лабораторной: {e}")
            return False

def get_student_tasks_with_status(user_id: int) -> list[tuple[int, str, bool]]:
    """
    Получает все задания студента по его user_id с информацией о выполнении.

    Args:
        user_id: ID студента

    Returns:
        Список кортежей (task_id, task_name, is_completed)
    """
    with Session() as session:
        # Получаем все subject_id, связанные с пользователем
        user_group = session.query(User).filter_by(id=user_id).first()
        student_subjects = session.query(GroupSubject.subject_id) \
            .filter(GroupSubject.group_id == user_group.group_rel.id) \
            .all()

        if not student_subjects:
            return []

        # Извлекаем только subject_id из результатов запроса
        subject_ids = [subj.subject_id for subj in student_subjects]

        # Получаем все задания, связанные с этими subject_id
        tasks = session.query(Task) \
            .filter(Task.Subject_id.in_(subject_ids)) \
            .order_by(Task.id) \
            .all()

        # Формируем результат с информацией о выполнении
        result = []
        for task in tasks:
            completed = is_task_completed(session, user_id, task.id)
            result.append((task.id, task.name, completed))

        return result

def get_lab_details(lab_id: int) -> dict | None:
    """
    Получает информацию о неопубликованной лабораторной работе, включая тестовые кейсы.

    :param lab_id: ID лабораторной работы
    :return: Словарь с информацией о лабораторной работе и её тестовых кейсах, если найдена, иначе None
    """
    with Session() as session:
        try:
            lab = session.query(Task).filter_by(id=lab_id).first()
            if not lab:
                return None

            # Формируем данные лабораторной работы
            lab_details = {
                "id": lab.id,
                "name": lab.name,
                "description": lab.description,
                "teacher_formula": lab.teacher_formula,
                "input_variables": lab.input_variables,
                "subject_id": lab.Subject_id,
                "test_cases": []
            }

            # Получаем тестовые кейсы, связанные с лабораторной работой
            test_cases = session.query(TestCase).filter_by(Task_id=lab_id).all()
            for test_case in test_cases:
                lab_details["test_cases"].append({
                    "id": test_case.id,
                    "input": test_case.inp,
                    "output": test_case.out
                })

            return lab_details

        except Exception as e:
            print(f"Error retrieving unpublished lab details: {e}")
            return None

def edit_lab(task_id: int, lab: UpdateLabRequest):
    """
    Обновляет информацию о лабораторной работе и её тест-кейсах.

    :param task_id: ID лабораторной работы
    :param lab: UpdateLabRequest с новыми данными
    :return: True, если обновление прошло успешно, иначе False
    """
    with Session() as session:
        try:
            # Получаем лабораторную работу по ID
            lab_to_update = session.query(Task).filter_by(id=task_id).first()
            if not lab_to_update:
                return False

            # Обновляем данные лабораторной работы
            lab_to_update.name = lab.task.name
            lab_to_update.description = lab.task.description
            lab_to_update.teacher_formula = lab.task.teacher_formula
            lab_to_update.input_variables = lab.task.input_variables
            lab_to_update.Subject_id = lab.task.subject_id

            # Удаляем старые тест-кейсы
            session.query(TestCase).filter_by(Task_id=task_id).delete()

            # Добавляем новые тест-кейсы
            for test_case in lab.task.test_cases:
                new_test_case = TestCase(
                    inp=test_case.inp,
                    out=test_case.out,
                    Task_id=task_id
                )
                session.add(new_test_case)

            # Сохраняем изменения в базе данных
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f"Ошибка при обновлении лабораторной работы: {e}")
            return False