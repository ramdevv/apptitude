# writing all the crud functions which would be imported
from db import connection
from models import (
    CreateUser,
)  # this is a pydantic model and it will be used to get the value of the createuser into the user modle which would be user to retrieve the data and update it

import secrets


def register_user(name: str, email: str, hashed_password: str):
    with connection.cursor() as cur:  # this will get us the acess to the db
        cur.execute(
            """ INSERT INTO users(name, email, hashed_password) VALUES(%s, %s, %s) RETURNING id;""",
            (name, email, hashed_password),
        )
        connection.commit()  # commit needs to save the inserted values
        return cur.fetchone()


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
        curr.execute("SELECT name FROM users WHERE email = %s", (email,))
        result = curr.fetchone()
        if result:
            return result[0]
        return None


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
