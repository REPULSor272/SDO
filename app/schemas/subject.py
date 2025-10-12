from pydantic import BaseModel

class SubjectInfo(BaseModel):
    id: int
    name: str
    grade: float | None

class LabStatus(BaseModel):
    id: int
    title: str
    status: str  # "Не выполнено", "Провалено", "Сдано"