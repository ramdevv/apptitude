# writing all the crud functions which would be imported
from db import connection
from fastapi import Request, Depends, HTTPException
from dotenv import load_dotenv
import json
import os
import jwt
import inspect

from models import (
    CreateUser,
)  # this is a pydantic model and it will be used to get the value of the createuser into the user modle which would be user to retrieve the data and update it

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


def get_hashed_password(email: str):
    with connection.cursor() as curr:
        curr.execute("SELECT hashed_password FROM users WHERE email = %s", (email,))
        result = curr.fetchone()
        if result:
            return result[0]
        return None
    # in this code we have added the comma after the email to treat this as a tupple and so we can add more parameters in the future


def check_user_by_email(email: str):
    with connection.cursor() as curr:
        curr.execute(
            "SELECT id, name, hashed_password FROM users WHERE email = %s", (email,)
        )
        result = curr.fetchone()
        if result:
            user_data = {"id": result[0], "name": result[1]}
            return user_data
        return None


"""
def give_user_authtoken(name: str):
    login_token = secrets.token_urlsafe(32)  # this generates a random id
    with connection.cursor() as curr:
        curr.execute(
            "UPDATE users SET auth_token = %s WHERE name = %s RETURNING name",
            (login_token, name),
        )
        result = curr.fetchone()
        connection.commit()  # this saves the response

        if result:
            return result[0]
        return None

"""


def read_json_file(file_path):
    """
    this function reads the content of the json file which you give the file path to
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)  # this will load all the data in the file
            return data
    except FileNotFoundError:
        print(
            f"Error the file {file_path} was not found"
        )  # this is how you write exeptions which can occure in the code
        return None
    except json.JSONDecodeError:
        print(f"Error: the file {file_path} could not be decode")
        return None


"""
# function to find the file_path in youre project
def find_path(name_of_file: str):
    callers_frame = inspect.stack([1])
    callers_file = (
        callers_frame.filename
    )  # this is the file where the function is called
    caller_dir = os.path.dirname(os.path.abspath(callers_file))

    return os.path.join(caller_dir, name_of_file)


# now lets try to call this function
"""


def register_user(name: str, email: str, hashed_password: str):
    with connection.cursor() as cur:  # this will get us the acess to the db
        cur.execute(
            """ INSERT INTO users(name, email, hashed_password) VALUES(%s, %s, %s) RETURNING id;""",
            (name, email, hashed_password),
        )
        connection.commit()  # commit needs to save the inserted values
        return cur.fetchone()


# function to write to fill all the content of the knowledge base base for the user


def insert_into_knowledge_base(raw_text: str, email: str):
    with connection.cursor() as cur:
        # to get the user from the username
        cur.execute("SELECT id FROM users WHERE email = %s ", (email,))
        user = cur.fetchone()
        if not user:
            raise Exception(" the user does not exist in the user table")
        user_id = user[0]
        # now that we have the id in which a user has beed inserted in the system then we can inset the raw text for rag implimentation
        cur.execute(
            "INSERT INTO knowledge_base (data, user_id) VALUES (%s, %s)",
            (raw_text, user_id),
        )
        connection.commit()


def get_current_user(request: Request):
    # to ask the fronend to send the token
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=404, detail="not authenticated")
    try:
        playload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token is expiered")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail=" invalid token")
    return playload
