from fastapi import FastAPI
from routes import auth
from utils import CreateUser
from routes import resume
import google.generativeai as genai

app = FastAPI()

# Register the router with /auth prefix
app.include_router(auth.auth_router, prefix="/auth")
app.include_router(resume.resume_handling, prefix="/resume")
