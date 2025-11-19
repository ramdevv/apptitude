from fastapi import APIRouter, Request, HTTPException, status
from utils import (
    get_data_from_knowledge_base,
    get_current_user,
    get_data_from_users,
    insert_question_data,
<<<<<<< HEAD
)
from dotenv import load_dotenv
=======
    get_user_quiz_answers,
    start_new_session,
    get_latest_session_id,
    insert_quiz_questions,
    insert_user_answers,
)
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
>>>>>>> feature/quiz_collection
import google.generativeai as genai
import os
import json
import re


questions_routes = APIRouter()

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

<<<<<<< HEAD
=======
""" 
format in which we will be getting the answers from the frontend will be :
{
"user_id : 1, 
answers = [{

"question": " what is youre name ,
"option": ["shubham", "garv", "karan"],
"selected" : "shubha" }, 

{and then the list of dicts goes on}]
}
"""


class Answers(BaseModel):
    session_id: int
    quiz_id: int
    user_id: int
    answers: dict

>>>>>>> feature/quiz_collection

@questions_routes.get("/Get_data_from_kb")
def Get_data_from_kb(request: Request):
    print("the data of the current user is:")
    current_usr_id = get_current_user(request)
    print(current_usr_id)
    data = get_data_from_users(current_usr_id["id"])
    return data


<<<<<<< HEAD
=======
@questions_routes.post("/create_session")
def create_session(request: Request):
    """
    this function makes an empty quiz session and returns a session id which will be given to insert the
    questions and then anwers
    """
    current_user_id_dict = get_current_user(request)
    current_user_id = current_user_id_dict["id"]
    # create a new quiz_session
    response = start_new_session(current_user_id)
    return response


>>>>>>> feature/quiz_collection
# this route will create the questions and the answers to it
@questions_routes.post("/create_technical")
async def create_technical(request: Request):
    # take the job profile that the user wants
    data = await request.json()
    user_job_porfile = data.get("job_profile", "software engeneer")
<<<<<<< HEAD
=======
    session_id = data.get("session_id")
    print(session_id)
>>>>>>> feature/quiz_collection
    current_user_id = get_current_user(request)
    resume_analysis = get_data_from_users(current_user_id["id"])
    prompt = f"""
    You are an expert technical evaluator and assessment designer.

    You will be provided with:
    1. A **job profile description**.
    2. A **detailed JSON analysis of a candidate's resume**.

    Your task:
    Generate a set of **10 multiple-choice technical questions** that evaluate both:
    - The candidate's **existing technical strengths** (from their resume analysis).
    - The **target job role's required skills** (from the provided job profile).

    ### Quiz Design Requirements:
    1. **Coverage balance:**
    - ~60% of questions should be based on the candidate’s current skills and experiences.
    - ~40% should be based on the job profile’s expected technologies or new skill areas.
    - If the resume and job role overlap heavily, evenly distribute questions across both areas.
    2. **Question composition:**
    - Each question must have **exactly 4 distinct answer options**.
    - Include **the correct answer explicitly** in a separate `"answer"` field.
    - Maintain consistent difficulty as per `"quiz_level"` from the resume analysis.
    3. **Bridge questions:**
    - Include 1–3 “bridge” questions that connect resume skills with target job skills (e.g., Python → Java OOP parallels).
    4. **JSON format only:**
    - Output must be valid JSON — no markdown, no commentary, no extra text.
    5. **Metadata for each question:**
    - `"topic"`: derived from either `"final_quiz_topics"`, `"assessment_areas"`, or inferred from the job profile.
    - `"difficulty"`: equal to `"quiz_level"` from the resume analysis.
    - `"source"`: one of `"resume"`, `"job_profile"`, or `"bridge"` to indicate question origin.

    ### Inputs:
    - Job Profile: {user_job_porfile}
    - Resume Analysis JSON: {resume_analysis}

    ### Expected Output Format:
    {{
    "questions": [
        {{
        "question": "What is the role of a Dockerfile in application deployment?",
        "options": [
            "It defines environment variables only",
            "It stores source code for deployment",
            "It specifies instructions to build a Docker image",
            "It manages Docker containers at runtime"
        ],
        "answer": "It specifies instructions to build a Docker image",
        "topic": "Containerization (Docker)",
        "difficulty": "intermediate",
        "source": "resume"
        }},
        {{
        "question": "Which annotation is used to define a REST controller in Spring Boot?",
        "options": [
            "@RestController",
            "@RequestHandler",
            "@APIEndpoint",
            "@WebMapping"
        ],
        "answer": "@RestController",
        "topic": "Java Backend Fundamentals (Spring Boot)",
        "difficulty": "intermediate",
        "source": "job_profile"
        }},
        {{
        "question": "Which programming concept is common to both Python and Java OOP?",
        "options": [
            "Encapsulation",
            "Duck Typing",
            "Dynamic Typing",
            "Scripting"
        ],
        "answer": "Encapsulation",
        "topic": "OOP Concepts (Python ↔ Java)",
        "difficulty": "intermediate",
        "source": "bridge"
        }}
    ]
    }}
    """
    response = model.generate_content(prompt)
    question_list = response.text
    try:
        # Remove code block formatting if Gemini adds it
        cleaned_json = re.sub(r"^```json\n|\n```$", "", question_list.strip())
        # Convert string to a dict
        parsed_json = json.loads(cleaned_json)
        only_questions = parsed_json["questions"]
<<<<<<< HEAD
        print("before inserting")
        insert_question_data(
            current_user_id["id"], category="technical", questions=only_questions
        )
=======
        print("inserted technical questions")
        quiz_id = insert_quiz_questions(session_id, "technical", only_questions)
>>>>>>> feature/quiz_collection
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing AI response: {str(e)}\nRaw response: {question_list}",
        )

<<<<<<< HEAD
    return {"questions": only_questions}
=======
    return {"questions": only_questions, "quiz_id": quiz_id}
>>>>>>> feature/quiz_collection


# this route will create the apptitude related questions for the user
@questions_routes.post("/create_apptitude")
<<<<<<< HEAD
def create_apptitude(request: Request):
=======
async def create_apptitude(request: Request):

    data = await request.json()
    session_id = data.get("session_id")
>>>>>>> feature/quiz_collection
    current_user = get_current_user(request)
    resume_analysis = get_data_from_users(current_user["id"])

    prompt = f"""
    You are an expert psychometric and aptitude test designer.

    You will be provided with:
    1. A **detailed JSON analysis** of a candidate’s resume, which includes their skill areas, experience level, and quiz difficulty level.
    2. Your task is to generate a **personalized aptitude test** that matches the user’s cognitive and professional level.

    ---

<<<<<<< HEAD
    ### 🎯 Task:
=======
    ### Task:
>>>>>>> feature/quiz_collection
    Generate **10 multiple-choice aptitude questions** that assess general intelligence, reasoning, and problem-solving abilities.

    The questions must include:
    - **5 General Aptitude Questions** — purely logical, numerical, or verbal reasoning questions of increasing difficulty.
    - **5 Resume-Aligned Aptitude Questions** — aptitude questions that *indirectly relate* to the candidate’s professional background or skills mentioned in the provided resume analysis (e.g., pattern recognition using code logic, data interpretation using tables, estimation involving project timelines, or verbal reasoning using technical scenarios).

    ---

<<<<<<< HEAD
    ### 🧠 Design Rules:
=======
    ###  Design Rules:
>>>>>>> feature/quiz_collection

    1. **Difficulty Adaptation:**
    - The difficulty must align with the candidate’s `"quiz_level"` (e.g., beginner, intermediate, advanced).
    - If `"quiz_level"` is missing, infer it from experience or seniority in the resume analysis.
    - Difficulty progression:
        - First 3 questions → Easy
        - Next 4 questions → Medium
        - Last 3 questions → Hard
    - Ensure both general and resume-aligned sets follow this progression.

    2. **Category Distribution:**
    - Logical reasoning: ~40%
    - Numerical reasoning: ~40%
    - Verbal reasoning: ~20%

    3. **Relevance & Resume Integration:**
    - For the 5 **resume-aligned** questions, create reasoning problems inspired by the user’s technical or domain background (from `resume_analysis`).
        Examples:
        - A logical flow question referencing debugging or data flow.
        - A numerical estimation question based on project timelines or performance metrics.
        - A verbal reasoning question using professional communication tone or terminology.
    - Avoid directly testing technical skills — the focus is still aptitude.

    4. **Answer Format:**
    - Each question must have **exactly 4 distinct answer options**.
    - Include the correct answer in an `"answer"` field.
    - Add a `"source"` field with value `"general"` or `"resume_based"`.

    5. **Output Format:**
    - Output **pure JSON only** (no markdown or explanations).
    - Each question must include:
        - `"question"`
        - `"options"` (list of 4 strings)
        - `"answer"`
        - `"type"`: one of `["logical", "numerical", "verbal"]`
        - `"difficulty"`: `"easy"`, `"medium"`, or `"hard"`
        - `"source"`: `"general"` or `"resume_based"`

    ---

    ### Inputs:
    Resume Analysis JSON: {resume_analysis}

    ---

    ### Example Output:
    {{
    "questions": [
        {{
        "question": "If a train travels 120 km in 2 hours, how long will it take to travel 300 km at the same speed?",
        "options": ["3 hours", "4 hours", "5 hours", "6 hours"],
        "answer": "5 hours",
        "type": "numerical",
        "difficulty": "easy",
        "source": "general"
        }},
        {{
        "question": "A developer completes a module in 5 days. If each subsequent module takes 20% less time, how many days for the 3rd module?",
        "options": ["3.2", "3.5", "4.0", "4.5"],
        "answer": "3.2",
        "type": "numerical",
        "difficulty": "medium",
        "source": "resume_base
        }},
        {{
        "question": "Choose the grammatically correct sentence:",
        "options": [
            "Each of the files have been uploaded.",
            "Each of the files has been uploaded.",
            "Each of file has been uploaded.",
            "Each file have been uploaded."
        ],
        "answer": "Each of the files has been uploaded.",
        "type": "verbal",
        "difficulty": "easy",
        "source": "general"
        }}
    ]
    }}
    """
    response = model.generate_content(prompt)
    question_list = response.text
    try:
        # Remove code block formatting if Gemini adds it
        cleaned_json = re.sub(r"^```json\n|\n```$", "", question_list.strip())
        # Convert string to a dict
        parsed_json = json.loads(cleaned_json)
        only_questions = parsed_json["questions"]
<<<<<<< HEAD
=======
        quiz_id = insert_quiz_questions(session_id, "apptitude", only_questions)
>>>>>>> feature/quiz_collection
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing AI response: {str(e)}\nRaw response: {question_list}",
        )

<<<<<<< HEAD
    return {"questions": only_questions}
=======
    return {"questions": only_questions, "quiz_id": quiz_id}
>>>>>>> feature/quiz_collection


# this route will create the apptitude related questions for the user
@questions_routes.post("/create_communication")
<<<<<<< HEAD
def create_communication():
=======
async def create_communication(request: Request):

    data = await request.json()
    session_id = data.get("session_id")
    current_user = get_current_user(request)
>>>>>>> feature/quiz_collection

    prompt = f"""
    You are an expert psychometric test designer specializing in **professional communication assessment**.

    Your goal is to generate **10 multiple-choice questions** that evaluate a candidate’s ability to communicate effectively and professionally in real-world workplace contexts.

    ---

<<<<<<< HEAD
    ### 🎯 Core Objective:
=======
    ### Core Objective:
>>>>>>> feature/quiz_collection
    Design questions that measure the candidate’s ability to convey, interpret, and adapt communication appropriately across professional scenarios such as meetings, emails, team collaborations, client interactions, and feedback discussions.

    ---

<<<<<<< HEAD
    ### 🧠 Skill Areas to Cover (balanced coverage required):
=======
    ###  Skill Areas to Cover (balanced coverage required):
>>>>>>> feature/quiz_collection
    1. **Clarity & Conciseness** – Expressing ideas effectively and efficiently.
    2. **Active Listening** – Understanding and recalling information accurately.
    3. **Written Communication** – Grammar, tone, structure, and professionalism in written correspondence.
    4. **Verbal Communication** – Articulation, tone, and response in spoken interactions.
    5. **Non-Verbal Interpretation** – Recognizing and responding appropriately to body language and expressions.
    6. **Adaptability** – Adjusting communication style to suit audience and context.
    7. **Conflict Resolution** – Using communication to manage disagreements professionally.
    8. **Professional Etiquette** – Appropriate use of language and tone in workplace communication.
    9. **Following Instructions** – Accurately interpreting and executing communicated directions.
    10. **Summarization & Paraphrasing** – Condensing or rephrasing key points effectively.

    ---

    ### 🧩 Question Design Rules:
    1. Each question must be based on a **realistic workplace scenario** (e.g., email exchange, team conversation, client update).
    2. Avoid grammar-only or trivia-type questions — focus on **judgment, reasoning, and communication awareness**.
    3. Maintain varied difficulty:
    - 3 easy (basic understanding)
    - 4 medium (applied reasoning)
    - 3 hard (complex or situational)
    4. Each question must include:
    - `"question"`: The text of the question.
    - `"options"`: Exactly 4 distinct answer choices.
    - `"answer"`: The correct answer text.
    - `"skill_area"`: One of the 10 skill areas above.
    - `"difficulty"`: `"easy"`, `"medium"`, or `"hard"`.

    ---

<<<<<<< HEAD
    ### 📄 Output Format:
=======
    ### Output Format:
>>>>>>> feature/quiz_collection
    Output **only valid JSON** — no markdown, no commentary, no explanations.

    Example:
    {{
    "questions": [
        {{
        "question": "During a team meeting, you notice a colleague repeatedly interrupts others. What is the most professional way to handle this?",
        "options": [
            "Ignore it and continue speaking",
            "Confront them directly during the meeting",
            "Wait for your turn and address it privately afterward",
            "Complain to HR immediately"
        ],
        "answer": "Wait for your turn and address it privately afterward",
        "skill_area": "Conflict Resolution",
        "difficulty": "medium"
        }},
        {{
        "question": "Which of the following best demonstrates active listening during a one-on-one conversation?",
        "options": [
            "Interrupting to share your point",
            "Maintaining eye contact and summarizing what the speaker said",
            "Taking notes silently without feedback",
            "Nodding occasionally without speaking"
        ],
        "answer": "Maintaining eye contact and summarizing what the speaker said",
        "skill_area": "Active Listening",
        "difficulty": "easy"
        }}
    ]
    }}

    Now, using this structure, generate 10 such questions **along with their correct answers**, fully formatted in pure JSON.
    """
    response = model.generate_content(prompt)
    question_list = response.text
    try:
        # Remove code block formatting if Gemini adds it
        cleaned_json = re.sub(r"^```json\n|\n```$", "", question_list.strip())
        # Convert string to a dict
        parsed_json = json.loads(cleaned_json)
        only_questions = parsed_json["questions"]
<<<<<<< HEAD
=======
        quiz_id = insert_quiz_questions(session_id, "communication", only_questions)
>>>>>>> feature/quiz_collection
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing AI response: {str(e)}\nRaw response: {question_list}",
        )

<<<<<<< HEAD
    return {"questions": only_questions}


# to write the route to create the total score of the quizes
=======
    return {"questions": only_questions, "quiz_id": quiz_id}


@questions_routes.post("/SubmitAnswers")
async def SubmitAnswers(answers_data: Answers):

    answer_id = insert_user_answers(
        answers_data.session_id,
        answers_data.quiz_id,
        answers_data.user_id,
        answers_data.answers,
    )
    return {"answer_id": answer_id}
>>>>>>> feature/quiz_collection
