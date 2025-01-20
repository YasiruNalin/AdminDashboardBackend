from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import traceback
import os
import sqlite3
import tempfile
from typing import List
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from app.services import load_and_split_documents, update_chromadb, initialize_chromadb, vectordb, persist_directory, embedding_model
from config import OPENAI_API_KEY

router = APIRouter()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup database connection
DATABASE_PATH = './chat_history_db/conversations.db'
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# Create conversations table if it doesn't exist
with sqlite3.connect(DATABASE_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_query TEXT,
        answer TEXT,
        sources TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

class Query(BaseModel):
    question: str

    
@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        
        content = await file.read()
        file_path = f'./new_papers/{file.filename}'
        with open(file_path, 'wb') as f:
            f.write(content)

        texts = load_and_split_documents('./new_papers/')
        vectordb = update_chromadb(texts, persist_directory, embedding_model)
        return {"filename": file.filename, "status": "Processed"}
    except Exception as e:
        logger.error(f"Error uploading or processing PDF: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to upload or process PDF")


@router.post("/query/")
async def query_rag(query: Query):
    try:
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(
                model_name='gpt-3.5-turbo',
                temperature=1,
                openai_api_key=OPENAI_API_KEY
            ),
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        response = qa_chain.invoke(query.question)

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO conversations (user_query, answer, sources)
            VALUES (?, ?, ?)
            """, (query.question, response['result'], ', '.join([doc.metadata['source'] for doc in response['source_documents']])))
            conn.commit()

        return {"answer": response['result'], "sources": [doc.metadata['source'] for doc in response['source_documents']]}
    except Exception as e:
        logger.error(f"Error querying RAG: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to process the query")


