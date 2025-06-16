from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import requests

app = FastAPI()

# CORS for frontend access (e.g., CodePen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your OpenAI key
openai.api_key = "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"  # <--- your API key here

# Input format
class CompareRequest(BaseModel):
    origin: str
    destination: str
    month: str

# Simple geocoding (Open-Meteo API)
def get_coords(place):
    res = requests.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": place})
    results = res.json().get("results")
    if not results:
        return None
    return results[0]["latitude"], results[0]["longitude"]

# Fetch daily temperature from Open-Meteo (historical)
def get_weather_data(lat, lon, month):
    return requests.get("https://archive-api.open-meteo.com/v1/archive", params={
        "latitude": lat,
        "longitude": lon,
        "start_date": f"2023-{month.lower()}-01",
        "end_date": f"2023-{month.lower()}-28",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }).json()

@app.post("/compare")
def compare(req: CompareRequest):
    origin_coords = get_coords(req.origin)
    dest_coords = get_coords(req.destination)

    if not origin_coords or not dest_coords:
        return {"error": "Unable to find coordinates for one of the locations."}

    origin_data = get_weather_data(*origin_coords, req.month)
    destination_data = get_weather_data(*dest_coords, req.month)

    # Build GPT prompt
    gpt_prompt = f"""
Compare the climate between {req.origin} and {req.destination} in {req.month} based on this data:

{req.origin} max temps: {origin_data['daily']['temperature_2m_max'][:5]}
{req.destination} max temps: {destination_data['daily']['temperature_2m_max'][:5]}

Summarize how they compare in terms of heat and comfort.
"""

    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a helpful weather assistant."},
            {"role": "user", "content": gpt_prompt}
        ]
    )

    summary = gpt_response["choices"][0]["message"]["content"]

    return {
        "summary": summary,
        "origin_data": origin_data,
        "destination_data": destination_data
    }
