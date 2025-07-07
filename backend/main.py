# backend/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from model_selector import route_query  # make sure this exists in the same folder

app = FastAPI()

# Allow requests from frontend (e.g., Streamlit or browser)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input schema
class QueryInput(BaseModel):
    question: str

# Root endpoint
@app.get("/")
def root():
    return {"message": "SkyQuery AI Help Bot is running!"}

# Main POST endpoint for frontend
@app.post("/ask")
def ask(query: QueryInput):
    print(f"Received question: {query.question}")  # Add this line
    response = route_query(query.question)
    return {"answer": response}

# Optional alias for backward compatibility
@app.post("/query")
def query_compat(query: QueryInput):
    return ask(query)
