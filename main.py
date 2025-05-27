from fastapi import FastAPI
from routes import auth
from utils import CreateUser

app = FastAPI()

# Register the router with /auth prefix
app.include_router(auth.auth_router, prefix="/auth")



