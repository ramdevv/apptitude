from pydantic import BaseModel  # this lib is used for data validation


class CreateUser(BaseModel):
    name: str
    email: str
    password: str


class users(BaseModel):
    id: int
    name: str
    email: str
    hashed_password: str
    auth_token: str
