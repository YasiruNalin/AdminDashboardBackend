import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from fastapi.responses import HTMLResponse
from app.routes import router
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify that the API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
print(api_key)
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

class Scenario(BaseModel):
    name:str

class Scenarios(BaseModel):
    scenarios: List[Scenario]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scenarios")
def get_scenarios():
    return {
        "scenarios": [
            {"name": "Scenario 1"},
            {"name": "Scenario 2"},
            {"name": "Scenario 3"}
        ]
    }
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)