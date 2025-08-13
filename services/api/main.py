import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
import sys

# Add rag_system to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from rag_system.retrieval.searcher import Searcher
from rag_system.generation.generator import Generator
from rag_system.generation.prompts import create_analysis_prompt

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Path to the index file with embeddings
INDEX_PATH = Path(__file__).parent.parent.parent / "apps/plain-check-web/public/data/guidelines.with_embeddings.json"

searcher = Searcher(INDEX_PATH)
generator = Generator()

class SearchQuery(BaseModel):
    query: str
    top_k: int = 3

@app.post("/search")
def search(query: SearchQuery):
    results = searcher.search(query.query, top_k=query.top_k)
    return {"results": results}

class CheckBody(BaseModel):
    text: str

@app.post("/check")
def check(body: CheckBody):
    # 1. Retrieve relevant guidelines
    guidelines = searcher.search(body.text, top_k=3)
    context = [g["text"] for g in guidelines]

    # 2. Generate a response from the LLM
    system_prompt, user_prompt = create_analysis_prompt(body.text, context)
    
    llm_response = generator.generate(user_prompt, context)

    # 3. Format the response as a single finding
    finding = {
        "ruleId": "llm-analysis",
        "title": "LLM-Powered Analysis",
        "message": llm_response,
        "severity": "info",
    }

    return {"findings": [finding]}

@app.get("/")
def read_root():
    return {"message": "RAG-RAG API is running."}