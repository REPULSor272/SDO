from pydantic import BaseModel


class User(BaseModel):
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    password: str = ""
    roleType: str = "Не указано"
    studyGroup: str = "Не указано"
    faculty: str = "Не указано"
    form_education: str = "Не указано"


class UserStatus(BaseModel):
    status: str = "Не указано"


class UserInfo(BaseModel):
    id: int = 0
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    studyGroup: str = "Не указано"


class FullUserInfo(BaseModel):
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    study_group: str = "Не указано"
    faculty: str = "Не указано"
    form_education: str = "Не указано"