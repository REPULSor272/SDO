from pydantic import BaseModel

class ResponseTest(BaseModel):
    status: str
    formulas_output: str
    code_output: str
    execution_time: float
    code_length: int