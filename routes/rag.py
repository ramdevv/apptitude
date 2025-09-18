# implimentation of rag

# to get the data and then turn them into chunks
import bs4  # lib to parse html and xml docunments
from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import vector_stores
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain.schema import Document
from langchain_cohere import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever

from typing_extensions import List, TypedDict
from pydantic import BaseModel
from utils import get_current_user, get_data_from_knowledge_base
import google.generativeai as genai
import os
import inspect
import json


load_dotenv()

rag_router = APIRouter()

# to get the cohere api key in the variable
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

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
    embedding_length=768,
    embeddings=embeddings,
    collection_name="resume_embeddings",
)


@rag_router.post("/save_text")
async def save_text(request: Request):
    # to take the user input of the quarrie that the user  wants to send
    # user_question = input_data.text_content

    try:
        # to call the resume from the knwoledge base in the database
        current_user = get_current_user(request)
        current_user_id = current_user["id"]
        raw_data_from_knowledge_base = get_data_from_knowledge_base(current_user_id)
        document = []  # this is initialised as a list

        # this is where all the text will get accumilated and will be parsed to the splitter
        for docs in raw_data_from_knowledge_base:
            doc = Document(
                page_content=docs["text"], metadata={"user_id": str(current_user_id)}
            )
            document.append(doc)

        # the raw data from the knowledge base is returning a list of dict which can not be passed in the spillter so we are splittin every
        text_splitters = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        all_splits = text_splitters.split_documents(document)
        """
        -> vector_store is the db which saves all the vectore embeddings 
        -> add_documents is the function which converts youre chunks into vectore embeddings 

        """
        ids = vector_stores.add_documents(all_splits)

        return {"message": ids}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
-> in this route we will be giving the prompt and with context we will get a response
-> this would take the quarrie that we have sent to it and get the context from the knowled_base and give the quarrie to the llm with the context
"""

# function for reranking using cohere


def rerank_docs(quarrie: str, candidate_docs: list[Document]):
    cohere_rerank = CohereRerank(
        cohere_api_key=COHERE_API_KEY, model="rerank-english-v3.0"
    )
    raw_text = [doc.page_content for doc in candidate_docs]
    reranked = cohere_rerank.rerank(query=quarrie, documents=raw_text)

    results = []
    for r in reranked:  # r is a dict, not object
        doc = candidate_docs[r["index"]]  # use dict key
        results.append(
            {
                "text": doc.page_content,
                "metadata": doc.metadata,
            }
        )

    return results


@rag_router.post("/context_chat")
async def context_chat(request: Request):
    # to get the current user id
    current_user = get_current_user(request)
    current_user_id = current_user["id"]

    user_quarrie = await request.json()
    question = user_quarrie.get("question")
    if not user_quarrie:
        raise HTTPException(status_code=400, detail="the questions were not found")
    # to retrieve the context using langchain
    retrieve_docs = vector_stores.similarity_search(
        query=question, k=3, filter={"user_id": str(current_user_id)}
    )

    pages = [doc.page_content for doc in retrieve_docs]
    docs_content = "\n\n".join(pages)
    reranked_docs = rerank_docs(question, retrieve_docs)
    raw_context_string = "\n\n".join(doc["text"] for doc in reranked_docs)
    print(raw_context_string)

    prompt_templat = """
            You are an AI assistant. Use the following context to answer the user’s question.

            Context:
            {context_text}

            Question:
            {question}

            Answer concisely and accurately based only on the context above. If the answer is not in the context, say "I don’t know."
            """

    context_prompt = prompt_templat.format(
        context_text=raw_context_string, question=question
    )
    response = model.generate_content(context_prompt)

    return {"reranked_docs ": raw_context_string, "ai_response": response.text}
