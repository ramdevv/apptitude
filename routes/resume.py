import pytesseract
import os
from PIL import Image
from fastapi import APIRouter, File, UploadFile, HTTPException
import google.generativeai as genai
from dotenv import load_dotenv

resume_handling = APIRouter()


load_dotenv()  # this calls all the variables in the .env file

# Configure the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model
model = genai.GenerativeModel("gemini-2.5-flash")


@resume_handling.post("/upload")
async def load_image_from(uploaded_file: UploadFile = File(...)):
    print(f"uploaded filename: {uploaded_file.filename}")
    print(f" content type : {uploaded_file.content_type}")
    allowed_file_types = ["image/png", "image/jpeg", "image/jpg"]
    if uploaded_file.content_type not in allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail="invalid file type. please give the input in the requested file type",
        )
    try:
        image = Image.open(uploaded_file.file)
        text = pytesseract.image_to_string(image)

        response = model.generate_content(
            f"""
        You are an expert technical evaluator. Analyze the following resume text provided in the variable {text}. Your tasks are:
	1.	Identify the candidate’s strong suits - list technical skills, projects, tools, and domains where the candidate shows depth.
	2.	Evaluate the candidate’s readiness for today’s software industry - check if their knowledge aligns with modern software development trends and tools.
	3.	Determine the most relevant areas for assessment - suggest topics and skill areas that should be tested in a quiz to evaluate this candidate further for software jobs.
	4.	Indicate the appropriate level of quiz complexity - beginner, intermediate, or advanced - based on their current profile.
        """
        )
        return {"analysis": response.text}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"image processing failed: {str(e)}",  # to conver the (error) into a string before it is printed
        )
