import pydantic

class User(pydantic.BaseModel):
    username: str
    password: str

class UserDb(pydantic.BaseModel):
    id: int
    username: str
    hash_password: str

    class Config:
        orm_mode = True


class Token(pydantic.BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class LogoutResponse(pydantic.BaseModel):
    result: str
