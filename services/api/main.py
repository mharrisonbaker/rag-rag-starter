
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
import sys

# Add rag_system to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from rag_system.retrieval.searcher import Searcher
from rag_system.generation.generator import Generator
from rag_system.compliance.rules import lint

app = FastAPI()

# Add CORS middleware
origins = [
    "https://www.plainlangeval.com",
    "https://plainlangeval.com",
    "https://mharrisonbaker-git-openai-generator-patex-machinas-projects.vercel.app",
    "http://localhost:5173", # For local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
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
    print(f"Received text for checking: {body.text[:100]}...") # Add logging
    findings = lint(body.text)
    print(f"Linting found {len(findings)} issues.") # Add logging
    
    for finding in findings:
        print(f"Searching for guideline for: {finding['query_for_guideline']}") # Add logging
        guidelines = searcher.search(finding["query_for_guideline"], top_k=1)
        if guidelines:
            context = [g["text"] for g in guidelines]
            suggestion = generator.generate(finding["title"], context)
            finding["suggestion"] = suggestion
        else:
            finding["suggestion"] = "No specific guideline suggestion found."

    print(f"Returning {len(findings)} findings.") # Add logging
    return {"findings": findings}

@app.get("/")
def read_root():
    return {"message": "RAG-RAG API is running."}
