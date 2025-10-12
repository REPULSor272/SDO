from pydantic import BaseModel

class TokenData(BaseModel):
    username: str
    first_name: str
    last_name: str
    middle_name: str
    group: str
    role: str
