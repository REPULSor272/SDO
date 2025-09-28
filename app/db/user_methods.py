from sqlite3 import IntegrityError
from typing import Any, Union
from app.db.db import Group, GroupSubject, Session, Subject, TeacherHasGroups, User, Task
from app.db.group_methods import get_group_id
from app.schemas.auth import RegisterRequest
from app.schemas.subject import SubjectInfo
from app.schemas.users import User as UserSchema


def get_groups_by_user_id(user_id: int) -> list[tuple[Any, Any]]:
    with Session() as session:
        groups = (
            session.query(Group.name, Group.id)
            .join(TeacherHasGroups, TeacherHasGroups.group_id == Group.id)
            .filter(TeacherHasGroups.teacher_id == user_id)
            .all()
        )
        response = []
        for group in groups:
            if group.name != "-":
                response.append((group.id, group.name))
        return response

def get_username_by_id(student_id: int) -> Union[str, None]:
    with Session() as session:
        user = session.query(User).filter_by(id=student_id).first()
        if user:
            return user.username
        return None


def get_users():
    """
    Получает всех пользователей из базы данных.

    :return: Список пользователей (объекты класса User)
    """
    with Session() as session:
        try:
            users = session.query(User).all()  # Получаем всех пользователей
            return users  # Возвращаем список пользователей
        except Exception as e:
            print(f"Error retrieving users: {e}")
            raise

def get_users_by_subject(subject_id):
    """
    Возвращает всех пользователей, зачисленных на предмет с заданным subject_id.

    :param subject_id: ID предмета
    :return: Список пользователей (объекты класса User)
    """
    with Session() as session:
        try:
            # Получаем предмет по его ID
            subject = session.query(Subject).filter_by(id=subject_id).first()
            if not subject:
                raise ValueError(f"Subject with ID {subject_id} not found.")

            # Получаем всех пользователей, зачисленных на данный предмет
            users = subject.users  # Используем связь many-to-many, определенную в модели

            return users  # Возвращаем список пользователей
        except Exception as e:
            print(f"Error retrieving users for subject {subject_id}: {e}")
            raise

def add_user_test(username, password, role_type='student', study_group='', form_education='-',
                  first_name='Иван', last_name='Иванов', middle_name='Иванович'):
    """
    Добавляет нового пользователя в базу данных.
    :param first_name:
    :param last_name:
    :param middle_name:
    :param form_education:
    :param username: Имя пользователя (уникальное)
    :param password: Пароль пользователя
    :param role_type: Роль пользователя (по умолчанию 'student')
    :param study_group: Учебная группа пользователя (опционально)
    :raises ValueError: Если пользователь с таким именем уже существует
    """
    # Проверка обязательных параметров
    if not username or not password:
        raise ValueError("Username and password are required fields.")

    # Создание сессии
    with Session() as session:
        try:
            # Проверка существующего пользователя с таким именем
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                raise ValueError(f"User with username '{username}' already exists.")

            # Создание нового пользователя
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                username=username,
                password=password,
                roleType=role_type,
                form_education=form_education,
                Group_id=study_group
            )
            session.add(new_user)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error adding user: {e}")
            raise


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

def add_user(register_data: RegisterRequest) -> Union[dict, str]:
    """
    Adds a new user to the database.

    :param register_data: The data of the user to be added.
    :param username: The username of the user.
    :param password: The password of the user.
    :param Group_id: The study group of the user.
    :return: A dictionary with user information if the user is added successfully, or an error message.
    """
    group_id = get_group_id(register_data.group_name)
    if not group_id:
        return "Group not found"

    middle_name = register_data.middle_name
    if middle_name == "-":
        middle_name = ""

    role_type = "student"
    if register_data.group_name == "vasiliy":
        role_type = "teacher"

    new_user = User(
        first_name=register_data.first_name,
        last_name=register_data.last_name,
        middle_name=middle_name,
        username=register_data.username,
        password=register_data.password,
        roleType=role_type,
        form_education='Бюджет',
        studyGroup=group_id,
    )

    with Session() as session:
        try:
            session.add(new_user)
            session.commit()
            return {
                "user_id": new_user.id,
                "username": new_user.username,
                "roleType": new_user.roleType,
                "form_education": new_user.form_education,
                "studyGroup": new_user.studyGroup
            }
        except IntegrityError:
            session.rollback()
            return "User not added"

def get_user_subjects(username: str) -> list[SubjectInfo]:
    """
    Получает все дисциплины, на которые зачислен пользователь (без фильтрации по статусу лабораторных).

    :param username:
    :return: Список дисциплин, на которые зачислен пользователь
    """
    with Session() as session:
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user or not user.group_rel:
                return []

            # Получаем id всех предметов группы пользователя
            group_subject_ids = session.query(GroupSubject.subject_id).filter_by(group_id=user.group_rel.id).all()
            subject_ids = [item.subject_id for item in group_subject_ids]

            # Получаем все предметы по id
            subjects = (
                session.query(Subject)
                .filter(Subject.id.in_(subject_ids))
                .all()
            )

            return [SubjectInfo(id=subject.id, name=subject.name, grade=0) for subject in subjects]

        except Exception:
            return []

def get_user_data(username: str) -> UserSchema:
    """
    Получает всю информацию о пользователе по его имени пользователя.

    :param username: Имя пользователя.
    :return: Объект UserSchema с информацией о пользователе, если он существует, иначе пустой UserSchema.
    """
    with Session() as session:
        user = session.query(User).filter_by(username=username).first()

        if user:
            # Проверяем, есть ли группа и факультет
            study_group_name = user.group_rel.name if user.group_rel else "Не указано"
            faculty_name = (
                user.group_rel.faculty_rel.name
                if user.group_rel and user.group_rel.faculty_rel
                else "Не указано"
            )

            return UserSchema(
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                password=user.password,
                roleType=user.roleType,
                studyGroup=study_group_name,
                faculty=faculty_name,
                form_education=user.form_education,
            )
        return UserSchema()  # Предполагается, что UserSchema имеет значения по умолчанию

def is_user_enrolled_in_subject(username: str, subject_id: int) -> bool | str:
    """
    Проверяет, зачислен ли пользователь на предмет по его ID.

    :param username:
    :param subject_id: ID или имя предмета
    :return: True, если пользователь зачислен на предмет, иначе False
    """
    with Session() as session:
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                return "User not found"

            user_subject_list = [subject.id for subject in user.group_rel.subjects]

            if not user_subject_list:
                return "No subjects found"

            return subject_id in user_subject_list

        except Exception as e:
            return f"Error checking enrollment for user {username} in subject {subject_id}: {e}"

def validate_user(username: str, password: str) -> Union[dict, bool]:
    """
    Validates the username and password of a user.

    :param username: The username of the user.
    :param password: The password of the user.
    :return: True if the username and password match, False otherwise.
    """
    with Session() as session:
        user = session.query(User).filter_by(username=username).first()
        if user and user.password == password:
            return {
                "user_id": user.id,
                "username": user.username,
                "roleType": user.roleType,
                "studyGroup": user.studyGroup
            }
        return False

