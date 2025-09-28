from typing import Type, Union
from app.db.db import Group, GroupSubject, Session, Solution, Subject, User, Task
from app.db.group_methods import get_groups_by_faculty
from app.db.task_methods import is_task_completed
from app.schemas.subject import LabStatus
from app.schemas.task import SolutionInfo, TaskInfo
from app.schemas.users import UserInfo
from sqlalchemy import func, case


def reg_user_in_subject(user_id, subject_identifier):
    """
    Зачисляет пользователя на дисциплину по ID пользователя и ID или имени дисциплины.

    :param user_id: ID пользователя
    :param subject_identifier: ID или имя дисциплины
    :raises ValueError: Если пользователь или дисциплина не найдены
    """
    with Session() as session:
        try:
            # Проверяем, существует ли пользователь с таким user_id
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                raise ValueError(f"User with ID {user_id} not found.")

            # Если передан ID дисциплины
            if isinstance(subject_identifier, int):
                subject = session.query(Subject).filter_by(id=subject_identifier).first()
            # Если передано имя дисциплины
            else:
                subject = session.query(Subject).filter_by(name=subject_identifier).first()

            if not subject:
                raise ValueError(f"Subject with identifier '{subject_identifier}' not found.")

            # Проверяем, не зачислен ли уже пользователь на эту дисциплину
            if subject in user.subjects:
                raise ValueError(f"User with ID {user_id} is already enrolled in the subject '{subject.name}'.")

            # Добавляем дисциплину в список предметов пользователя
            user.subjects.append(subject)
            session.commit()

        except Exception as e:
            session.rollback()  # Откат транзакции в случае ошибки
            print(f"Error enrolling user {user_id} in subject {subject_identifier}: {e}")
            raise

def get_users_by_group(group_id) -> list[UserInfo] | str:
    with Session() as session:
        users = session.query(User).filter_by(studyGroup=group_id).all()

        if not users:
            return f"No users found for group with ID {group_id}."

        users_info: list[UserInfo] = []
        for user in users:
            user_info = UserInfo(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                studyGroup=user.group_rel.name,
            )
            users_info.append(user_info)

        return users_info


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
            .filter(Task.Subject_id.in_(subject_ids), Task.status=='published') \
            .order_by(Task.id) \
            .all()

        # Формируем результат с информацией о выполнении
        result = []
        for task in tasks:
            completed = is_task_completed(session, user_id, task.id)
            result.append((task.id, task.name, completed))

        return result

def get_student_labs_by_subject(student_id: int, subject_id: int) -> list[LabStatus]:
    """
    Получает список лабораторных работ студента по предмету с их статусами.

    :param student_id: ID студента.
    :param subject_id: ID предмета.
    :return: Список объектов LabStatus с информацией о заданиях и их статусах.
    """
    with Session() as session:
        # Основной запрос
        labs_status = (
            session.query(
                Task.id.label("task_id"),
                Task.name.label("task_name"),
                func.coalesce(
                    func.max(
                        case(
                            (Solution.status == "Success", "Сдано"),
                            (Solution.status == "Failed", "Провалено"),
                            else_="Не выполнено"
                        )
                    ), "Не выполнено"
                ).label("status")
            )
            .outerjoin(
                Solution,
                (Task.id == Solution.Task_id) & (Solution.User_id == student_id)
            )
            .filter(Task.Subject_id == subject_id)
            .group_by(Task.id, Task.name)
            .all()
        )

        result = [
            LabStatus(
                id=row.task_id,
                title=row.task_name,
                status=row.status
            )
            for row in labs_status
        ]

        return result


def get_student_labs(student_id: int, lab_id: int) -> TaskInfo | str:
    """
    Получает детальную информацию о лабораторной работе студента, включая статус и все его решения.

    :param student_id: ID студента.
    :param lab_id: ID лабораторной работы (Task).
    :return: Объект LabDetailResponse с информацией о задании и решениях.
    """
    with Session() as session:
        # Проверяем существование задания
        task = session.query(Task).filter_by(id=lab_id).first()
        if not task:
            return f"Лабораторная работа с ID {lab_id} не найдена"

        # Получаем статус задания для студента
        status_query = (
            session.query(
                func.coalesce(
                    func.max(
                        case(
                            (Solution.status == "Success", "Сдано"),
                            (Solution.status == "Failed", "Провалено"),
                            else_="Не выполнено"
                        )
                    ), "Не выполнено"
                ).label("status")
            )
            .filter(Solution.User_id == student_id)
            .filter(Solution.Task_id == lab_id)
        ).scalar()

        # Получаем все решения студента для этого задания
        solutions = (
            session.query(Solution)
            .filter(Solution.User_id == student_id)
            .filter(Solution.Task_id == lab_id)
            .all()
        )

        if not solutions:
            return f"No solutions found for student with ID {student_id} and task with ID {lab_id}."
        print([(solution.code, solution.status) for solution in solutions])
        # Формируем список решений
        solutions_list = [
            SolutionInfo(
                code=solution.code,
                status=solution.status if solution.status else "Не выполнено",
            )
            for solution in solutions
        ]

        # Формируем ответ
        response = TaskInfo(
            id=task.id,
            name=task.name,
            description=task.description,
            count_subtasks=1,
            status=status_query,
            solutions=solutions_list
        )

        return response

def get_users_by_faculty(faculty_id: int) -> Union[list[UserInfo], str]:
    """
    Получает список студентов, связанных с факультетом через их группы.

    :param faculty_id: ID факультета.
    :return: Список объектов UserInfo или сообщение об ошибке, если студентов нет.
    """
    with Session() as session:
        groups = get_groups_by_faculty(faculty_id)

        if not groups:
            return f"No groups found for faculty with ID {faculty_id}."

        users = []
        for group in groups:
            group_users = session.query(User).filter_by(studyGroup=group.id).all()
            for user in group_users:
                user_info = UserInfo(
                    id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    middle_name=user.middle_name,
                    studyGroup=user.group_rel.name,
                )
                users.append(user_info)

        if not users:
            return f"No users found for faculty with ID {faculty_id}."

        return users
