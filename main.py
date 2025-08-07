from fastapi import FastAPI
from routes import auth, resume, questions
from utils import CreateUser
from app_cache import init_redis_cache
from contextlib import asynccontextmanager
import google.generativeai as genai


# now we will initialise the cache in this line
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis_cache()
    yield


app = FastAPI(lifespan=lifespan)


# Register the router with /auth prefix
app.include_router(auth.auth_router, prefix="/auth")
app.include_router(resume.resume_handling, prefix="/resume")
app.include_router(questions.questions_router, prefix="/questions")
