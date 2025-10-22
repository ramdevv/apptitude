import os
import smtplib
import jwt
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


from fastapi import APIRouter, Request, Response
from werkzeug.security import generate_password_hash, check_password_hash
from utils import (
    register_user,
    get_hashed_password,
    check_user_by_email,
)

from models import CreateUser


load_dotenv()  # this is done do load all the .env variables from youre env file
SECRET_KEY = os.getenv("SECRET_KEY")


auth_router = APIRouter()


@auth_router.post("/register")
def register_new_user(users: CreateUser):

    name = users.name  # all the data which is passed through the CreateUser moodel will
    email = users.email  # get converted into the a users data object that i can acess
    user_password = users.password
    print("before")
    if check_user_by_email(email):
        return {"error", "there is already a username with the entered email"}
    else:
        print("there is some one who is the same ")

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


@auth_router.post("/login")
def login_user(users: CreateUser, response: Response):
    # take the input of the user
    name = users.name
    email = users.email
    password = users.password  # this is the users password
    result = check_user_by_email(email)
    if result:
        hashed_password = get_hashed_password(email)
        if not check_password_hash(hashed_password, password):
            return {"error": "the password is invalid"}
        # writing the jwt when the user is authenticated
        payload = {
            "id": result["id"],
            "name": result["name"],
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=2),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=7200,
            expires=7200,
            samesite="lax",
            secure=False,
        )
        return {"message": " the user has logged in succesfully"}
    return {"error": " the user was not found"}
