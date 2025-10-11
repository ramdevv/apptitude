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
from pdf2image import convert_from_bytes  # <-- Added for PDFs

from utils import get_current_user, insert_into_knowledge_base

import uuid

resume_handling = APIRouter()

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


@resume_handling.post("/upload")
async def load_image_from(request: Request, uploaded_file: UploadFile = File(...)):
    print(f"uploaded filename: {uploaded_file.filename}")
    print(f"content type : {uploaded_file.content_type}")

    allowed_file_types = ["image/png", "image/jpeg", "image/jpg", "application/pdf"]

    if uploaded_file.content_type not in allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image or PDF.",
        )

    try:
        contents = await uploaded_file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # for handleing the pdf type as pytessereact is not able to read a pdf image
        if uploaded_file.content_type == "application/pdf":
            try:
                pages = convert_from_bytes(contents)
                text = ""
                for page in pages:
                    text += pytesseract.image_to_string(page)
            except Exception as pdf_err:
                raise HTTPException(
                    status_code=400, detail=f"Failed to process PDF: {str(pdf_err)}"
                )

        # for handleing the image
        else:
            try:
                image = Image.open(BytesIO(contents))
                image.load()
                text = pytesseract.image_to_string(image)
            except Exception as img_err:
                raise HTTPException(
                    status_code=400, detail=f"Failed to process image: {str(img_err)}"
                )

        data = {"text": text}
        raw_text = json.dumps(data)
        print("Extracted text:", raw_text)

        # Get current user
        current_user = get_current_user(request)
        current_user_id = current_user["id"]

        # Insert into knowledge base
        try:
            insert_into_knowledge_base(raw_text, current_user_id)
        except Psycopg2Error as db_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(db_error)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error inserting resume: {str(e)}",
            )

        prompt = f"""
        You are a highly skilled technical evaluator and career assessment expert. The candidate's target role is **Junior Python Backend Developer**.

        **TASK:** Analyze the candidate's resume below and generate a tailored quiz preparation plan.

        **RESUME CONTENT:**
        {text}

        **INSTRUCTIONS:**
        1. Analyze strengths & projects.
        2. Evaluate readiness for production backend standards.
        3. Identify missing skills or weak areas.
        4. Suggest an intermediate quiz plan for skill improvement.

        **OUTPUT FORMAT (STRICT JSON ONLY):**
        {{
        "strong_suits": ["<list all strong technical skills and tools>", "..."],
        "projects": ["<list all key projects>", "..."],
        "industry_readiness": "<short assessment, typically 2-3 sentences>",
        "assessment_areas": ["<list all high-level areas to test>", "..."],
        "final_quiz_topics": ["<list the specific, intermediate-level topics to be tested>", "..."],
        "quiz_level": "intermediate",
        "reasoning": "<clear justification for the selected topics>"
        }}
        """

        response = model.generate_content(prompt)
        analysis_text = response.text

        return {
            "message": "Resume processed and added into the knowledge base successfully.",
            "analysis": analysis_text,
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Image processing failed: {str(e)}",
        )
