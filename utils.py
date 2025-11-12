# writing all the crud functions which would be imported
from db import connection, vector_connection
from fastapi import Request, Depends, HTTPException
from dotenv import load_dotenv
from psycopg2.extras import Json
from pydantic import BaseModel, Field
import json
import re
import os
import jwt
import inspect
import json
import re
from fastapi import HTTPException

from models import (
    CreateUser,
)  # this is a pydantic model and it will be used to get the value of the createuser into the user modle which would be user to retrieve the data and update it

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


class user_id_Class(BaseModel):
    user_id: int = Field(..., description="this calss only takes an integer")


class RegUserClass(BaseModel):
    name: str
    email: str
    hashed_password: str


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


def register_user(user_att: RegUserClass):
    with connection.cursor() as cur:  # this will get us the acess to the db
        cur.execute(
            """ INSERT INTO users(name, email, hashed_password) VALUES(%s, %s, %s) RETURNING id;""",
            (user_att.name, user_att.email, user_att.hashed_password),
        )
        connection.commit()  # commit needs to save the inserted values
        return cur.fetchone()


# function to write to fill all the content of the knowledge base base for the user


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


def get_data_from_knowledge_base(user_id: int):
    with connection.cursor() as cur:
        try:
            cur.execute(
                "SELECT data FROM knowledge_base WHERE user_id = %s;", (user_id,)
            )
            rows = cur.fetchall()  # fetch all rows for that user_id
            return [row[0] for row in rows]  # extract only the 'data' values
        except Exception as e:
            raise Exception(f"error fetching the data from the knowledge_base: {e}")


def insert_into_knowledge_base(raw_text: str, user_id: int):
    with connection.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO knowledge_base (data, user_id) VALUES (%s, %s)",
                (raw_text, user_id),
            )
            connection.commit()
            print("the data is inserted into the knowledge_base")
        except Exception as e:
            connection.rollback()  # this is done to fix the error " the current transaction is aborted"
            raise Exception(
                f"there is an error inserting the error in the knowledge_base: {e}"
            )


def insert_json_into_users(json_data: dict, user_id: int):
    with connection.cursor() as cur:
        try:
            # this will clean Gemini's output
            cleaned = re.sub(r"```json|```", "", json_data).strip()

            # convert the cleaned string into a Python dict
            json_python_dict = json.loads(cleaned)

            # convert the dict back to a valid JSON string for insertion
            cleaned_json = json.dumps(json_python_dict)

            cur.execute(
                "UPDATE users SET resume_analysis = %s WHERE id = %s",
                (cleaned_json, user_id),
            )
            connection.commit()
            print("the analysis is added into the users table")
            return cleaned_json
        except Exception as e:
            connection.rollback()
            # must specify status_code here; otherwise FastAPI complains
            raise HTTPException(
                status_code=500,
                detail=f"there has been some issue inserting the data in the db: {e}",
            )


def get_data_from_users(user_id: int):
    with connection.cursor() as cur:
        try:
            cur.execute("SELECT resume_analysis FROM users WHERE id = %s;", (user_id,))
            rows = cur.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"there is an error in fetching the data from the db: {e}",
            )


def insert_question_data(user_id: int, category: str, questions: dict | list):
    with connection.cursor() as cur:
        try:
            print("DEBUG types:", type(user_id), type(category), type(questions))

            cur.execute(
                "INSERT INTO quiz_questions (user_id, category, questions) VALUES (%s, %s, %s)",
                (user_id, category, json.dumps(questions)),
            )
            connection.commit()
            print(" The data has been added into the db")

        except Exception as err:
            connection.rollback()
            raise Exception(f"There was an error inserting the data in the db: {err}")


def get_user_quiz_answers(user_id=int):
    with connection.cursor() as cur:
        try:
            cur.execute(
                """
                SELECT 
                    user_quiz_answers.id,
                    quiz_questions.category,
                    user_quiz_answers.answers,
                    user_quiz_answers.score,
                    user_quiz_answers.submitted_at
                FROM user_quiz_answers
                JOIN quiz_questions
                ON user_quiz_answers.quiz_id = quiz_questions.id
                WHERE user_quiz_answers.user_id = %s
                ORDER BY user_quiz_answers.submitted_at DESC
                LIMIT 1
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            raise HTTPException(f" error fetching the quiz answers from the db : {e}")


# to write the function to insert the answers into the user_question_answers
def insert_user_answers(
    user_id: int, answers: dict | list, score: int, accuracy: float, quiz_id: int
):
    with connection.cursor() as cur:
        try:
            cur.execute(
                """
                    INSERT INTO user_quiz_answers (user_id, quiz_id, answers, score, accuracy)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                (user_id, quiz_id, json.dump(answers), accuracy),
            )
            connection.commit()
            print(" the answers have been added into the databse")
        except Exception as e:
            connection.rollback()
            raise HTTPException(
                status_code=500, detail=f"there there was some issue inserting the data"
            )


def get_latest_quiz_id(user_id: int):
    with connection.cursor() as cur:
        try:
            cur.execute(
                """
                SELECT id 
                FROM quiz_questions 
                WHERE user_id = %s
                ORDER BY generated_at DESC 
                LIMIT 1;
                """,
                (user_id,),
            )
            result = cur.fetchone()

            if result:
                quiz_id = result[0]
                print(f"the latest quiz id is this {quiz_id}")
                return quiz_id
            else:
                print(f"No quiz found for user {user_id}")
                return None

        except Exception as e:
            raise Exception(f"Error fetching latest quiz_id: {e}")
