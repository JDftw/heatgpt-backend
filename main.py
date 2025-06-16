from fastapi import FastAPI
from pydantic import BaseModel
import openai, requests

openai.api_key = "your-openai-api-key"

app = FastAPI()

class CompareRequest(BaseModel):
    origin: str
    destination: str
    month: str

@app.post("/compare")
def compare(req: CompareRequest):
    return {"summary": f"Mock comparison: {req.origin} vs {req.destination} in {req.month}"}
