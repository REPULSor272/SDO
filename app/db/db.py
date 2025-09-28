from typing import Union, Type, Any

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, Boolean, Float, func, case
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, InstrumentedAttribute
from sqlalchemy.dialects.postgresql import ENUM

from app.config.config import init_config
from app.schemas.auth import RegisterRequest
from app.schemas.subject import SubjectInfo, LabStatus
from app.schemas.teachers import TaskWithTestCasesSchema
from app.schemas.users import User as UserSchema, UserInfo
from app.schemas.task import Task as TaskSchema, Task, TaskInfo, SolutionInfo
import logging

logging.basicConfig(level=logging.CRITICAL)  # Глобально отключить все логи, кроме критических
for logger_name in ('sqlalchemy', 'sqlalchemy.engine', 'sqlalchemy.pool'):
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

# Database connection setup
cfg = init_config()['database']
DATABASE_URL = f"postgresql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['name']}"
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

RoleTypeEnum = ENUM('admin', 'teacher', 'student', name='role', create_type=True)


class TeacherHasGroups(Base):
    __tablename__ = 'TeacherHasGroups'
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('User.id'))
    group_id = Column(Integer, ForeignKey('Group.id'))
    user = relationship("User", back_populates="teacher_groups")
    group = relationship("Group", back_populates="teacher_groups")


class Faculty(Base):
    __tablename__ = 'Faculty'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    groups = relationship('Group', back_populates='faculty_rel')


class Group(Base):
    __tablename__ = 'Group'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True, nullable=False)
    faculty = Column(Integer, ForeignKey('Faculty.id'))
    faculty_rel = relationship('Faculty', back_populates='groups')
    users = relationship('User', back_populates='group_rel')
    subjects_link = relationship("GroupSubject", back_populates="group", overlaps="subjects")
    subjects = relationship("Subject", secondary="Group_Subject",
                            back_populates="groups",
                            overlaps="subjects_link,groups_link")
    teacher_groups = relationship("TeacherHasGroups", back_populates="group")


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    roleType = Column(String(10), nullable=False, default='student')
    studyGroup = Column(Integer, ForeignKey('Group.id', ondelete='CASCADE'))
    form_education = Column(String(255), nullable=False, default='Не указано')
    first_name = Column(String(64), nullable=False, default='Не указано')
    last_name = Column(String(64), nullable=False, default='Не указано')
    middle_name = Column(String(64), default='Не указано')
    group_rel = relationship('Group', back_populates='users')
    teacher_groups = relationship("TeacherHasGroups", back_populates="user")
    solutions = relationship('Solution', back_populates='user', cascade="all, delete-orphan")


class GroupSubject(Base):
    __tablename__ = 'Group_Subject'
    group_id = Column(Integer, ForeignKey('Group.id', ondelete='CASCADE'), primary_key=True)
    subject_id = Column(Integer, ForeignKey('Subject.id', ondelete='CASCADE'), primary_key=True)
    group = relationship("Group", back_populates="subjects_link", overlaps="subjects")
    subject = relationship("Subject", back_populates="groups_link", overlaps="groups,subjects")


class Subject(Base):
    __tablename__ = 'Subject'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    groups = relationship("Group", secondary="Group_Subject",
                          back_populates="subjects",
                          overlaps="subjects_link,groups_link")
    groups_link = relationship("GroupSubject", back_populates="subject", overlaps="groups,subjects")
    tasks = relationship('Task', back_populates='subject')

class Solution(Base):
    __tablename__ = 'Solution'
    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    mark = Column(Integer, nullable=True)
    lengthTestResult = Column(Boolean, nullable=True)
    formulaTestResult = Column(Boolean, nullable=True)
    autoTestResult = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    User_id = Column(Integer, ForeignKey('User.id', ondelete='CASCADE'), nullable=False)
    Task_id = Column(Integer, ForeignKey('Task.id', ondelete='CASCADE'), nullable=True)
    user = relationship('User', back_populates='solutions')
    task = relationship('Task', back_populates='solution', uselist=False)


class Task(Base):
    __tablename__ = "Task"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(String(2048), nullable=True)
    teacher_formula = Column(String, nullable=True)
    input_variables = Column(String, nullable=True)
    status = Column(String, nullable=False)
    Subject_id = Column(Integer, ForeignKey('Subject.id', ondelete='CASCADE'), nullable=False)
    subject = relationship('Subject', back_populates='tasks')
    solution = relationship('Solution', back_populates='task', uselist=False)
    testCases = relationship('TestCase', back_populates='task')


class TestCase(Base):
    __tablename__ = 'TestCase'
    id = Column(Integer, primary_key=True)
    inp = Column(String(512), nullable=False)
    out = Column(String(512), nullable=False)
    Task_id = Column(Integer, ForeignKey('Task.id', ondelete='CASCADE'), nullable=True)
    task = relationship('Task', back_populates='testCases')

def delete_tables():
    Base.metadata.drop_all(engine)


def create_tables():
    Base.metadata.create_all(engine)
