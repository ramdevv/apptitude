import pytesseract
import os
import json
import psycopg2
from PIL import Image
from fastapi import APIRouter, File, UploadFile, HTTPException, Request, status
import google.generativeai as genai
from psycopg2 import Error as Psycopg2Error
from dotenv import load_dotenv
from io import BytesIO

from utils import get_current_user, insert_into_knowledge_base
import random


import uuid

resume_handling = APIRouter()


load_dotenv()  # this calls all the variables in the .env file

# Configure the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model
model = genai.GenerativeModel("gemini-2.5-flash")


@resume_handling.post("/upload")
async def load_image_from(request: Request, uploaded_file: UploadFile = File(...)):
    print(f"uploaded filename: {uploaded_file.filename}")
    print(f" content type : {uploaded_file.content_type}")
    allowed_file_types = ["image/png", "image/jpeg", "image/jpg"]
    if uploaded_file.content_type not in allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail="invalid file type. please give the input in the requested file type",
        )
    try:
        contents = await uploaded_file.read()  # this reads the whole file
        if not contents:
            raise HTTPException(status_code=400, detail="empty file uploaded")
        image = Image.open(BytesIO(contents))
        image.load()  # this loads the image after it is completely opened

        text = pytesseract.image_to_string(image)
        data = {"text": text}
        raw_text = json.dumps(data)
        print(raw_text)

        # to insert the raw_text into the knowledge base
        # to get the current user
        current_user = get_current_user(request)
        current_user_id = current_user["id"]
        print("till this is ok")
        # to insert into the knowledge_base
        try:
            insert_into_knowledge_base(raw_text, current_user_id)

        except Psycopg2Error as db_error:
            # this is for all the db related errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f" databse error:{str(db_error)}",
            )
        except Exception as e:
            # this is for any other exception which is unexpected
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"there is some error inserting the reusme:{str(e)}",
            )

        # this prompt gets all of the resume and evalueates the user
        response = model.generate_content(
            f"""


            You are a highly skilled technical evaluator and career assessment expert. Your tasks are:

            1. Analyze the following resume text provided in the variable {text}.
            2. Identify the candidate’s strong suits – list technical skills, projects, tools, and domains where the candidate shows depth.
            3. Evaluate the candidate’s readiness for today’s software industry – check if their knowledge aligns with modern software development trends and tools.
            4. Determine the most relevant areas for assessment – suggest topics and skill areas that should be tested in a quiz to evaluate this candidate further for software jobs.

            Based on the analysis, and considering the job role the candidate wants to pursue which is **[INSERT TARGET JOB ROLE HERE, e.g., 'Junior Python Backend Developer']**, also generate a quiz preparation plan tailored to the candidate:
            5. Include the topics to be tested in the quiz and the difficulty level of the quiz.
            6. Only include topics that are directly relevant to the user’s desired job role and not already deeply mastered by the user.
            7. Use the resume’s suggested quiz level as a starting point, but feel free to raise or lower the level based on the complexity of the target job.
            8. Focus on topics that will help bridge the gap between the user’s current skills and the job requirements.

            **CRITICAL INSTRUCTION: Your entire response must be a single, well-formed JSON object. Do not add any text, markdown, or commentary outside of the JSON structure. If the analysis is long, ensure the JSON is not truncated. DO NOT use the JSON block formatting (```json...```).**

            Give your response in the following JSON format:

            {
            "strong_suits": ["<skill_1>", "<skill_2>", "..."],
            "projects": ["<project_1>", "<project_2>", "..."],
            "industry_readiness": "<short assessment>",
            "assessment_areas": ["<area_1>", "<area_2>", "..."],
            "final_quiz_topics": ["<topic_1>", "<topic_2>", "..."],
            "quiz_level": "beginner | intermediate | advanced",
            "reasoning": "<clear justification for selected topics and level>"
            }
            """
        )
        analysis_text = response.text

        return {
            "message": " the raw text has been added into the knowledge_base",
            "analysis": analysis_text,
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"image processing failed: {str(e)}",  # to conver the (error) into a string before it is printed
        )
