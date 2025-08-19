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
from typing_extensions import List, TypedDict
from pydantic import BaseModel
import google.generativeai as genai
import os

load_dotenv()

rag_router = APIRouter()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model
model = genai.GenerativeModel("gemini-2.5-flash")


class text_input(BaseModel):
    text_content: str


@rag_router.post("/data_to_chunks")
async def data_to_chunks(input_data: text_input):
    # to take the user input of the quarrie that the user  wants to send
    user_question = input_data.text_content
    # print(user_question)

    # this is how to make a document object in python
    """
    doc1 = Document(page_content=" the redis cache ")


    doc2 = Document(
        page_content=" this is the secone redis caceh ",
        metadata={"source": "example file", "page": 1},
    )
    print(doc2.metadata)

    """
    # to make a document of the redis cache which i have done of the data of the resume
    """
    for making the docume i have to get all the data which i have to get from the redis cache 

    """
    # first to retrive the user id of the currnet user
    redis = FastAPICache.get_backend().redis
    user_id = await redis.get("current user_id")
    if user_id:
        resume_text = await redis.get(f"user:{user_id}resume_raw_text")
    # print (resume_text)
    # to make a document object of the reusume_text
    doc1 = Document(
        page_content=resume_text, metadata={"source": "resume_text", "page": 1}
    )

    # now we have gotten the resume data we can make this into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents([doc1])
    # print(all_splits)
    # now that we have divided this into chunks we can
    _ = vector_stores.add_documents(document=all_splits)

    """
    -> vector_store is the db which saves all the vectore embeddings 
    -> add_documents is the function which converts youre chunks into vectore embeddings 

    """
    retrieved_docs = vector_stores.similarity_search(
        user_question
    )  # now we would find relevent chunks for youre quesiton
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)

    # the final prompt will contain the context and the user questoin

    final_prompt = f"""
You are an AI assistant. Answer the following question using only the context below.
If the answer is not in the context, say "I don't know."

Context:
{context_text}

Question:
{user_question}

Answer:
"""
    response = model.generate_content(final_prompt)

    return {"the response to youre question with context is:": response}
