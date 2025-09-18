import os  # this line is just written to communicate with the os
import psycopg  # this converts python variables/data_types into sql values using there types
from dotenv import load_dotenv  # this loads all the data in a .file


load_dotenv()  # this is just the function which is doing the loading of the .env file so we are able to acess the variables inside of it

connection = psycopg.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
)
vector_connection = psycopg.connect(
    host=os.getenv("vDB_HOST"),
    dbname=os.getenv("vDB_NAME"),
    user=os.getenv("vDB_USER"),
    password=os.getenv("vDB_PASSWORD"),
    port=os.getenv("vDB_PORT"),
)
