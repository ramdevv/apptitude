from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, resume, questions, rag
from utils import CreateUser
from contextlib import asynccontextmanager
import google.generativeai as genai


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    print("App is starting up ")
    yield
    # --- shutdown ---
    print("App is shutting down ")


app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing; use ["http://127.0.0.1:5500"] in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Register the routers
app.include_router(auth.auth_router, prefix="/auth")
app.include_router(resume.resume_handling, prefix="/resume")
app.include_router(questions.questions_router, prefix="/questions")
app.include_router(rag.rag_router, prefix="/rag")
