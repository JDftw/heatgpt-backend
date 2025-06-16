from fastapi import FastAPI
from pydantic import BaseModel
import openai, requests

openai.api_key = "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"

app = FastAPI()

class CompareRequest(BaseModel):
    origin: str
    destination: str
    month: str

@app.post("/compare")
def compare(req: CompareRequest):
    return {"summary": f"Mock comparison: {req.origin} vs {req.destination} in {req.month}"}
