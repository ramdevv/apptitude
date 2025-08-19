import pytesseract
import os
import json
from PIL import Image
from fastapi import APIRouter, File, UploadFile, HTTPException, Request
import google.generativeai as genai
from dotenv import load_dotenv


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

        image = Image.open(uploaded_file.file)
        text = pytesseract.image_to_string(image)

        # to make a randome id for the user
        user_id = str(uuid.uuid4())  # this would generate the randome id
        # print(user_id)

        # this prompt gets all of the resume and evalueates the user
        response = model.generate_content(
            f"""


            You are a highly skilled technical evaluator and career assessment expert. Your tasks are:

            1. Analyze the following resume text provided in the variable {text}.
            2. Identify the candidate’s strong suits – list technical skills, projects, tools, and domains where the candidate shows depth.
            3. Evaluate the candidate’s readiness for today’s software industry – check if their knowledge aligns with modern software development trends and tools.
            4. Determine the most relevant areas for assessment – suggest topics and skill areas that should be tested in a quiz to evaluate this candidate further for software jobs.

            Based on the analysis, and considering the job role the candidate wants to pursue which is , also generate a quiz preparation plan tailored to the candidate:
            5. Include the topics to be tested in the quiz and the difficulty level of the quiz.
            6. Only include topics that are directly relevant to the user’s desired job role and not already deeply mastered by the user.
            7. Use the resume’s suggested quiz level as a starting point, but feel free to raise or lower the level based on the complexity of the target job.
            8. Focus on topics that will help bridge the gap between the user’s current skills and the job requirements.
            9. Include reasoning that clearly shows how your choice of topics and level matches the candidate’s needs.

            Give your response in the following JSON format (do not add anything outside this JSON structure):

            {{
            "strong_suits": ["<skill_1>", "<skill_2>", "..."],
            "projects": ["<project_1>", "<project_2>", "..."],
            "industry_readiness": "<short assessment>",
            "assessment_areas": ["<area_1>", "<area_2>", "..."],
            "final_quiz_topics": ["<topic_1>", "<topic_2>", "..."],
            "quiz_level": "beginner | intermediate | advanced",
            "reasoning": "<clear justification for selected topics and level>"
            }}
            """
        )
        # make a json and write the resume content into it
        data_to_store = {"resume_content_raw": response.text}
        file_path = "routes/storage.json"
        with open(file_path, "w") as json_file:
            json.dump(data_to_store, json_file, indent=4)

        return {"analysis": response.text}

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"image processing failed: {str(e)}",  # to conver the (error) into a string before it is printed
        )
