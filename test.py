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
    allowed_file_types = ["image/png", "image/jpeg", "image/jpg", "image/pdf"]
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
        prompt = f"""
        You are a highly skilled technical evaluator and career assessment expert. The candidate's target role is **Junior Python Backend Developer**.

**TASK:** Analyze the candidate's resume (provided elsewhere) and generate a tailored quiz preparation plan.

**INSTRUCTIONS:**
1.  **Analyze Strengths & Projects:** Identify depth areas (Python frameworks, AI integration, Docker, MongoDB).
2.  **Evaluate Readiness:** Assess alignment with modern production standards (e.g., CI/CD, robust security, relational databases).
3.  **Determine Gaps:** Identify skills lacking depth for a production-ready Backend Developer (e.g., SQL, Cloud, Testing).
4.  **Tailor Quiz:** Select **Intermediate** level topics that bridge these gaps. Only include topics not already deeply mastered by the candidate.
5.  **quiz level** do not forget giving the quiz results in the response as it is very important 

**CRITICAL FORMAT ENFORCEMENT:**
Your entire response **MUST** strictly adhere to the JSON format provided below. **DO NOT** add any introductory text, concluding commentary, markdown formatting (like ```json), or any text outside of the JSON structure itself.

{{
"strong_suits": ["<list all strong technical skills and tools>", "..."],
"projects": ["<list all key projects>", "..."],
"industry_readiness": "<short assessment, typically 2-3 sentences>",
"assessment_areas": ["<list all high-level areas to test>", "..."],
"final_quiz_topics": ["<list the specific, intermediate-level topics to be tested>", "..."],
"quiz_level": "intermediate",
"reasoning": "<clear justification for the selected topics, level, and how they bridge the candidate's skill gaps>"
}}
        """
        response = model.generate_content(prompt)
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
