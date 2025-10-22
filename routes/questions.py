from fastapi import APIRouter, Request
from utils import get_data_from_knowledge_base, get_current_user, get_data_from_users

questions_routes = APIRouter()


@questions_routes.get("/Get_data_from_kb")
def Get_data_from_kb(request: Request):
    print("the data of the current user is:")
    current_usr_id = get_current_user(request)
    print(current_usr_id)
    data = get_data_from_users(current_usr_id["id"])
    return data
