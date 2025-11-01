from app.db.db import Session, Solution, Subject, TestCase
from app.db.subject_methods import get_subject_id_by_task
from app.schemas.task import Task as TaskSchema, TaskInfo, SolutionInfo
from app.db.db import Task, User


def get_task_data(task_id: int) -> dict | None:
    """
    Получает данные задачи по её ID.

    :param task_id: ID задачи
    :return: Словарь с данными задачи, если найдена, иначе None
    """
    with Session() as session:
        task = session.query(Task).filter_by(id=task_id).first()
        if task:
            return {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "teacher_formula": task.teacher_formula,
                "input_variables": task.input_variables
            }
        return None


def get_tasks_by_subject(subject_id: int) -> str | list[Task]:
    """
    Получает все задачи, связанные с предметом по его ID.

    :param subject_id: ID или имя предмета
    :return: Список задач, связанных с предметом
    :raises ValueError: Если предмет с таким идентификатором или именем не найден
    """
    with Session() as session:
        try:
            subject = session.query(Subject).filter_by(id=subject_id).first()

            if not subject:
                return "Subject not found"

            tasks = session.query(Task).filter_by(Subject_id=subject.id, status='published').order_by(Task.id).all()

            if not tasks:
                return "No tasks found for subject"

            return [TaskSchema(id=task.id, name=task.name, description=task.description) for task in tasks]

        except Exception as e:
            return str(e)


def get_test_cases_by_task(task_id):
    """
    Получает все тестовые случаи, связанные с задачей по её ID.

    :param task_id: ID задачи
    :return: Список тестовых случаев для указанной задачи
    :raises ValueError: Если задача с таким ID не найдена
    """
    with Session() as session:
        try:
            # Проверяем, существует ли задача с таким task_id
            task = session.query(Task).filter_by(id=task_id).first()
            if not task:
                raise ValueError(f"Task with ID {task_id} not found.")

            # Извлекаем все тестовые случаи, связанные с данной задачей
            test_cases = session.query(TestCase).filter_by(Task_id=task_id).all()

            # Если тестовые случаи не найдены, возвращаем пустой список
            if not test_cases:
                print(f"No test cases found for task with ID {task_id}.")
                return []

            return test_cases

        except Exception as e:
            print(f"Error retrieving test cases for task with ID {task_id}: {e}")
            raise


def get_user_solutions_by_task(user_id, task_id):
    """
    Получает все решения пользователя для конкретной задачи по ID.

    :param user_id: ID пользователя
    :param task_id: ID задачи
    :return: Список решений пользователя для указанной задачи
    :raises ValueError: Если решения не найдены для указанного пользователя и задачи
    """
    with Session() as session:
        try:
            # Запрос решений пользователя для конкретной задачи
            solutions = session.query(Solution).filter_by(User_id=user_id, Task_id=task_id, is_hidden =False).all()

            # Если решения не найдены, возвращаем пустой список или выбрасываем ошибку
            if not solutions:
                print(f"No solutions found for user {user_id} and task {task_id}.")
                return []

            return solutions
        except Exception as e:
            print(f"Error retrieving solutions for user {user_id} and task {task_id}: {e}")
            raise

def add_solution(code, user_id, task_id) -> str | bool:
    """
    Добавляет решение в базу данных.

    :param code: Код решения (обязательное поле)
    :param user_id: ID пользователя (обязательное поле)
    :param task_id: ID задачи (обязательное поле)
    :raises ValueError: Если код решения не указан
    """
    if not code:
        return "Code is a required field."

    # Получение subject_id по task_id
    subject_id = get_subject_id_by_task(task_id)
    if not subject_id:
        return "Task not found."

    # Проверка, прикреплен ли пользователь к предмету
    with Session() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return "User not found."

        group_subject_ids = [gs.subject_id for gs in user.group_rel.subjects_link]
        if subject_id not in group_subject_ids:
            return "User is not enrolled in the subject."

    # Создание сессии
    with Session() as session:
        try:
            # Создание нового решения
            solution = Solution(
                code=code,
                User_id=user_id,  # Привязка к пользователю
                Task_id=task_id  # Привязка к задаче
            )
            session.add(solution)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return "Error adding solution"


def update_solution_status(solution_id: int, status: str):
    with Session() as session:
        try:
            solution = session.query(Solution).filter_by(id=solution_id).first()
            if solution:
                solution.status = status
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error updating solution status: {e}")
            raise


def update_solution_hidden(user_id:int, solution_id: int):
    """Скрывает solution пользователя. Возвращает True, если успешно."""
    with Session() as session:
        try:
            solution = session.query(Solution).filter_by(User_id=user_id,
                id=solution_id).first()
            if not solution:
                return False
            solution.is_hidden = True
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"[update_solution_hidden] Error: {e}")
            return False

def get_solutions_by_user(user_id):
    """
    Получает все решения, связанные с пользователем по его ID.

    :param user_id: ID пользователя
    :return: Список решений пользователя
    :raises ValueError: Если пользователь с таким ID не найден
    """
    with Session() as session:
        try:
            # Получение всех решений пользователя
            solutions = session.query(Solution).filter_by(User_id=user_id).all()

            # Если решений не найдено, можно вернуть пустой список или выбросить исключение
            if not solutions:
                print(f"No solutions found for user with ID {user_id}.")
                return []

            return solutions
        except Exception as e:
            print(f"Error retrieving solutions for user with ID {user_id}: {e}")
            raise


def get_latest_solution(user_id: int, task_id: int) -> Solution | None:
    """
    Получает последнее решение пользователя для конкретной задачи.

    :param user_id: ID пользователя
    :param task_id: ID задачи
    :return: Последнее решение пользователя, если найдено, иначе None
    """
    with Session() as session:
        solution = session.query(Solution).filter_by(User_id=user_id, Task_id=task_id).order_by(
            Solution.id.desc()).first()
        return solution


def evaluate_solution(solution_id, new_mark):
    """
    Оценка решения пользователя для заданного решения.

    :param user_id: ID пользователя
    :param task_id: ID задачи
    :param new_mark: Новая оценка для решения
    :return: Строка с результатом обновления
    :raises ValueError: Если пользователь или задача не найдены, либо решение не найдено
    """
    with Session() as session:
        try:
            # Находим решение пользователя
            solution = session.query(Solution).filter_by(id=solution_id).first()
            if not solution:
                raise ValueError(f"No solution found for solution {solution_id}.")

            # Обновляем поле mark у найденного решения
            solution.mark = new_mark
            session.commit()  # Сохраняем изменения
            return True

        except Exception as e:
            session.rollback()  # Откатываем транзакцию в случае ошибки
            print(f"Error evaluating solution for {solution_id}: {e}")
            raise

def is_task_completed(session: Session, user_id: int, task_id: int) -> bool:
    """
    Проверяет, выполнено ли задание студентом.

    Args:
        session: Сессия SQLAlchemy
        user_id: ID студента
        task_id: ID задания

    Returns:
        True если есть хотя бы одно успешное решение, иначе False
    """
    # Проверяем наличие успешных решений (autoTestResult = 1)
    solution = session.query(Solution) \
        .filter(
        Solution.User_id == user_id,
        Solution.Task_id == task_id,
        Solution.status == "Success"  # 1 означает успешное выполнение
    ) \
        .first()

    return solution is not None