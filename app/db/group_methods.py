from typing import Type
from app.db.db import Faculty, Group, Session
from sqlalchemy.orm import InstrumentedAttribute

from app.schemas.users import User, UserInfo


def get_faculty_name(faculty_id):
    with Session() as session:
        faculty = session.query(Faculty).filter_by(id=faculty_id).first()
        if faculty:
            return faculty.name
        return None


def get_group_name(group_id):
    with Session() as session:
        group = session.query(Group).filter_by(id=group_id).first()
        if group:
            return group.name
        return None


def get_group_id(group_name: str) -> InstrumentedAttribute | None:
    with Session() as session:
        group = session.query(Group).filter_by(name=group_name).first()
        if group:
            return group.id
        return None


def get_faculty_by_group(group_id):
    with Session() as session:
        try:
            if isinstance(group_id, int):
                group = session.query(Group).filter_by(id=group_id).first()
            else:
                group = session.query(Group).filter_by(name=group_id).first()

            if not group:
                raise ValueError(f"Group '{group_id}' not found.")

            faculty = session.query(Faculty).filter_by(id=group.Faculty_id).first()
            return faculty

        except Exception as e:
            session.rollback()

def get_groups() -> list[str]:
    with Session() as session:
        groups = session.query(Group).all()
        result = []
        for group in groups:
            if group.name != "-":
                result.append(group.name)

        return result
    
def get_groups_by_faculty(faculty_id: int) -> list[Type[Group]] | str:
    with Session() as session:
        groups = session.query(Group).filter_by(faculty=faculty_id).all()

        if not groups:
            return f"No groups found for faculty with ID {faculty_id}."

        return groups

