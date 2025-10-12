from pydantic import BaseModel

class ResponseUpload(BaseModel):
    task_id: int