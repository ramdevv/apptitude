from fastapi import APIRouter, Request
from werkzeug.security import generate_password_hash, check_password_hash
from utils import register_user
from models import CreateUser

auth_router = APIRouter()


@auth_router.post("/register")
def register_new_user(users: CreateUser):

    name = users.name  # all the data which is passed through the CreateUser moodel will
    email = users.email  # get converted into the a users data object that i can acess
    user_password = users.password

    hashed_password = generate_password_hash(
        user_password, method="pbkdf2:sha256", salt_length=16
    )
    # print(hashed_password)

    value = register_user(
        users.name, users.email, hashed_password
    )  # fill the user objects into the register fucntion
    print(value)

    if isinstance(value, int):
        print("the login is succesfull")

    print(" the login was not succesfull")

    return {"name": name, "email": email}
