import os
import logging
import traceback
from typing import List

from fastapi import HTTPException
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader

persist_directory = './chromadb_storage/db'
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_split_documents(directory):
    loader = DirectoryLoader(directory, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    if not documents:
        logger.warning(f"No documents found in {directory}")
        return []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(documents)

def initialize_chromadb(directory, persist_directory):
    try:
        os.makedirs(directory, exist_ok=True)
        texts = load_and_split_documents(directory)
        if not texts:
            logger.warning("No texts to initialize ChromaDB. Creating an empty database.")
            vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)
        else:
            vectordb = Chroma.from_documents(documents=texts,
                                             embedding=embedding_model,
                                             persist_directory=persist_directory)
        vectordb.persist()
        return vectordb
    except Exception as e:
        logger.error(f"Error initializing ChromaDB: {e}")
        logger.error(traceback.format_exc())
        return None

def update_chromadb(texts, persist_directory, embedding_model):
    try:
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)
        vectordb.add_documents(documents=texts)
        vectordb.persist()
        return vectordb
    except Exception as e:
        logger.error(f"Error updating ChromaDB: {e}")
        logger.error(traceback.format_exc())
        return None

# Initialize vectordb
os.makedirs(persist_directory, exist_ok=True)
os.makedirs('./new_papers/', exist_ok=True)
vectordb = initialize_chromadb('./new_papers/', persist_directory)
if vectordb is None:
    logger.error("Failed to initialize ChromaDB")
    # You might want to handle this error case appropriately in your application