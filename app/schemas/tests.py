from pydantic import BaseModel

class TestCase(BaseModel):
    formulas_output: str
    code_output: str
    execution_time: float
    code_length: int
    execution_status: str
