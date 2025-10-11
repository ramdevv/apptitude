from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, resume, questions, rag
from utils import CreateUser
from contextlib import asynccontextmanager
import google.generativeai as genai
import sys
import uvicorn


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
    allow_origins=["http://localhost:3000"],  # for testing; use
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Function to run the app manually
def run_app():
    # Print the message if the app is being reloaded in development mode
    if "reload" in sys.argv:
        print("App is reloading...")

    # Get the port and URL info based on Uvicorn's config
    print("App is running at:")
    print("  - URL: http://localhost:8000/")
    print("  - To stop the server, press CTRL+C")


if __name__ == "__main__":
    # Start the server and print information
    run_app()

    # Run the FastAPI app using Uvicorn, with `--reload` for development mode
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


#  Register the routers
app.include_router(auth.auth_router, prefix="/auth")
app.include_router(resume.resume_handling, prefix="/resume")
# app.include_router(questions.questions_router, prefix="/questions")
app.include_router(rag.rag_router, prefix="/rag")
