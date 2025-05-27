# writing all the crud functions which would be imported
from db import connection
from models import (
    CreateUser,
)  # this is a pydantic model and it will be used to get the value of the createuser into the user modle which would be user to retrieve the data and update it


def register_user(name: str, email: str, hashed_password: str):
    with connection.cursor() as cur:  # this will get us the acess to the db
        cur.execute(
            """ INSERT INTO users(name, email, hashed_password) VALUES(%s, %s, %s) RETURNING id;""",
            (name, email, hashed_password),
        )
        connection.commit()  # commit needs to save the inserted values
        return cur.fetchone()
