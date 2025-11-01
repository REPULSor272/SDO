from pydantic import BaseModel

class SolutionInfo(BaseModel):
    id: int
    code: str = ""
    status: str = ""
    is_hidden: bool

class TaskInfo(BaseModel):
    id: int = 0
    name: str = ""
    description: str = ""
    count_subtasks: int = 0
    status: str = ""
    solutions: list[SolutionInfo] = []

class Task(BaseModel):
    id: int
    name: str
    description: str
    status: str = "Не выполнено"