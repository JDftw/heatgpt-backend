from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <-- add this
from pydantic import BaseModel
import openai, requests

app = FastAPI()

# 👇 Add this to allow frontend (like CodePen) to access your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = "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"

class CompareRequest(BaseModel):
    origin: str
    destination: str
    month: str

@app.post("/compare")
def compare(req: CompareRequest):
    return {
        "summary": f"Mock comparison: {req.origin} vs {req.destination} in {req.month}"
    }
