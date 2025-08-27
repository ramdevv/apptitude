# implimentation of rag

# to get the data and then turn them into chunks
import bs4  # lib to parse html and xml docunments
from langchain_core.documents import Document
from fastapi_cache import FastAPICache
from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import vector_stores
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

from typing_extensions import List, TypedDict
from pydantic import BaseModel
from utils import get_current_user, get_data_from_knowledge_base
import google.generativeai as genai
import os
import inspect
import json


load_dotenv()

rag_router = APIRouter()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model
model = genai.GenerativeModel("gemini-2.5-flash")

# to make the vectore databse connection
DATABASE_URL = "postgresql://garvituser:watermellon@localhost:5432/vectordb"

# this is the model that i am using to
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
# to initialise the pgvector
vector_stores = PGVector(
    connection=DATABASE_URL,
    embedding_length=1536,
    embeddings=embeddings,
    collection_name="resume_embeddings",
)


class text_input(BaseModel):
    raw_text: str


@rag_router.post("/save_text")
async def data_to_chunks(request: Request):
    # to take the user input of the quarrie that the user  wants to send
    # user_question = input_data.text_content
    try:
        # to call the resume from the knwoledge base in the database
        current_user = get_current_user(request)
        current_user_id = current_user["id"]
        raw_data_from_knowledge_base = get_data_from_knowledge_base(current_user_id)

        # to split into chuncks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = splitter.split_text(raw_data_from_knowledge_base)
        vector_stores.add_texts(chunks)
        return {"message": f" saved the {(chunks) } into the vectore databse"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    """
    -> vector_store is the db which saves all the vectore embeddings 
    -> add_documents is the function which converts youre chunks into vectore embeddings 

    """
