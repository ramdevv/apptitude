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
You are an expert in technical assessment. You will be provided with a job profile description. Based on this job profile, generate 10 multiple-choice technical questions designed to assess the candidate's relevant skills and knowledge.

The questions should be specific to the technologies, concepts, and practices typically required for the provided job profile. The questions should vary in difficulty, covering foundational to advanced concepts.

Each question must have:
- 4 distinct answer choices.
- One correct answer explicitly mentioned in the output.

Ensure the questions are relevant to the practical application of technical skills in the given job role. Focus on core technical competency that is required for the specified job.

After generating the questions, provide the correct answer for each question in the JSON under a field called `"answer"`.

Here is the job profile: {job_profile}

Output format: Return the result in **pure JSON format only**, without markdown or code block formatting.

Example:
{{
  "questions": [
    {{w
      "question": "What is the output of print(2 ** 3)?",
      "options": ["6", "8", "9", "5"],
      "answer": "8"
    }}
  ]
}}
"""
    response = model.generate_content(prompt)

    return {"the questions for the user ": response.text}


@questions_router.post("/get_apptitude")
async def get_apptitude():
    prompt = (
        new_prompt
    ) = """
        Generate 10 multiple-choice aptitude questions designed to assess a candidate's cognitive abilities. Cover the following areas: logical reasoning, numerical reasoning, and verbal reasoning. Each question must have 4 distinct answer choices. Ensure the questions vary in difficulty and cover a range of problem-solving skills relevant to a technical role. 
        Each question should have 4 distinct answer choices.
        Output the result in **pure JSON format** without any code block formatting.

        Example:
        {
          "questions": [
            {
              "question": "Your question here?",
              "options": ["Option A", "Option B", "Option C", "Option D"]
            }
          ]
        }
    """

    response = model.generate_content(prompt)
    return {"apptitude_questions": response}


@questions_router.post("/get_communication")
async def get_communication():
    prompt = """
            Okay, here's a prompt designed to generate 10 multiple-choice aptitude questions for assessing a candidate's communication skills:
                
                "You are an expert in communication assessment. Generate 10 multiple-choice questions designed to evaluate a candidate's communication skills. Cover the following areas:
                Clarity and Conciseness: Ability to express ideas effectively and efficiently.
                Active Listening: Comprehension and retention of information from spoken or written sources.
                Written Communication: Grammar, spelling, tone, and organization in written messages.
                Verbal Communication: Articulation, tone, and appropriateness in spoken interactions.
                Interpretation of Non-Verbal Cues: Understanding and responding to body language and facial expressions.
                Adaptability in Communication: Tailoring communication style to different audiences and situations.
                Conflict Resolution through Communication: Handling disagreements and finding common ground.
                Professional Email/Message Etiquette: Following conventions for formal and informal digital communication.
                Understanding and Following Instructions: Accurately processing and acting upon directions.
                Summarization and Paraphrasing: Ability to condense and rephrase information accurately.
                Each question must have 4 distinct answer choices. Ensure the questions vary in difficulty and cover a range of communication skills relevant to a professional role. Provide the question followed by the 4 answer choices. Do not provide the answer key."
            Output the result in **pure JSON format** without any code block formatting.

            Example:
            {
            "questions": [
                {
                "question": "Your question here?",
                "options": ["Option A", "Option B", "Option C", "Option D"]
                }
            ]
            }
        """

    response = model.generate_content(prompt)
    return {"the questions are": response}
