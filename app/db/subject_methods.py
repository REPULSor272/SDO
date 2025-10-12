from app.db.db import Session, Subject
from app.db.db import Task


def get_subject_id_by_task(task_id: int) -> int | None:
    """
    Получает subject_id по task_id.

    :param task_id: ID задачи
    :return: ID предмета, если найден, иначе None
    """
    with Session() as session:
        task = session.query(Task).filter_by(id=task_id).first()
        if task:
            return task.Subject_id
        return None


def add_subject(name):
    """
    Добавляет новый предмет в базу данных.

    :param name: Название предмета (уникальное)
    :raises ValueError: Если предмет с таким именем уже существует
    """
    if not name:
        raise ValueError("Subject name is required.")

    with Session() as session:
        try:
            # Проверка, существует ли уже предмет с таким именем
            existing_subject = session.query(Subject).filter_by(name=name).first()
            if existing_subject:
                raise ValueError(f"Subject with name '{name}' already exists.")

            # Создание нового предмета
            new_subject = Subject(name=name)
            session.add(new_subject)
            session.commit()
        except Exception as e:
            session.rollback()  # откат в случае ошибки
            print(f"Error adding subject: {e}")
            raise


def get_subjects():
    """
    Получает все предметы из базы данных.

    :return: Список всех предметов
    :raises Exception: Если произошла ошибка при извлечении данных
    """
    with Session() as session:
        try:
            # Извлечение всех предметов из базы данных
            subjects = session.query(Subject).all()

            # Если предметы не найдены, возвращаем пустой список
            if not subjects:
                print("No subjects found.")
                return []

            return subjects
        except Exception as e:
            print(f"Error retrieving subjects: {e}")
            raise
