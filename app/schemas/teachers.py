from pydantic import BaseModel
from typing import Optional, List
from app.schemas.task import SolutionInfo


class StudentResponse(BaseModel):
    id: int = 0
    full_name: str = "Не указано"
    studyGroup: str = "Не указано"

class GroupResponse(BaseModel):
    id: int = 0
    name: str = ""


class LabResponse(BaseModel):
    id: int = 0
    title: str = ""
    status: str = ""


class LabDetailResponse(BaseModel):
    id: int = 0
    name: str = ""
    description: str = ""
    count_subtasks: int = 0
    status: str = ""
    solutions: list[SolutionInfo] = []


class GroupResponse(BaseModel):
    id: int
    name: str = ""

#### создание лабы

# Модель для тесткейсов
class TestCaseSchema(BaseModel):
    id: int
    inp: str
    out: str

    class Config:
        from_attributes = True

# Базовая модель для Task без тестов
class TaskBaseSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    teacher_formula: Optional[str] = None
    input_variables: Optional[str] = None
    subject_id: int

    class Config:
        from_attributes = True

# Модель Task с тесткейсами
class TaskWithTestCasesSchema(TaskBaseSchema):
    test_cases: List[TestCaseSchema]


# Основная результирующая модель
class CreateLabRequest(BaseModel):
    task: TaskWithTestCasesSchema

    class Config:
        from_attributes = True

class LabResponse(BaseModel):
    id: int
    name: str
    subject_name: str
    status: str

class UpdateLabRequest(BaseModel):
    task: TaskWithTestCasesSchema

    class Config:
        from_attributes = True

class DetailLab(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    teacher_formula: Optional[str] = None
    input_variables: Optional[str] = None
    subject_id: int
    test_cases: List[TestCaseSchema]