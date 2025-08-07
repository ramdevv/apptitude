from fastapi import APIRouter, Request
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi_cache import FastAPICache


load_dotenv()  # calling this to load all the variables in the env file
questions_router = APIRouter()


# Configure the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model
model = genai.GenerativeModel("gemini-2.5-flash")


# router to generate the question for the quiz
@questions_router.post("/get_technical")
async def get_technical_questions(request: Request):
    redis = FastAPICache.get_backend().redis
    value = await redis.get("key")
    # now we have the value of all the analysis of the resume now we have to parse this for beter useage

    # first we have to clean the data
    cleaned = value.replace("```json\n", "").replace("```", "")
    # print(cleaned)

    # Step 2: Parse JSON string
    parsed = json.loads(cleaned)

    # Step 3: Use the parsed data
    # print(parsed)

    # now we can send the parsed data to the llm to generate a quiz for us
    data = await request.json()
    job_profile = data.get(
        "job_profile", "software_engenner"
    )  # the second one is given when the user has not entered the value of the value

    prompt = f"""
    "You are an expert in technical assessment. You will be provided with a job profile description. Based on this job profile, generate 10 multiple-choice technical questions designed to assess the candidate's relevant skills and knowledge.
    The questions should be specific to the technologies, concepts, and practices typically required for the provided job profile.
    The questions should vary in difficulty, covering foundational to advanced concepts.
    Each question must have 4 distinct answer choices.
    Ensure the questions are relevant to the practical application of technical skills in the given job role.
    Focus on core technical competency that is required for the specified job.
    After the questions have been generated, please do not provide the answer key. Only provide the questions with the multiple choice answers.
    For example: If the job description is "Software Engineer - Python Backend", the questions should be related to Python, backend development, APIs, databases, etc.
    Here is the job profile: {job_profile}
    Provide the question followed by the 4 answer choices. Do not provide the answer key."
    Output the result in **pure JSON format** without any code block formatting.

    Example:
    {{
    "questions": [
        {{
        "question": "Your question here?",
        "options": ["Option A", "Option B", "Option C", "Option D"]
        }}
    ]
    }}
"""
    response = model.generate_content(prompt)

    return {"the questions for the user ": response.text}
