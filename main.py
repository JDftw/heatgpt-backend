from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import openai
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create FastAPI app
app = FastAPI()

# ✅ Proper CORS middleware to fix 405 OPTIONS error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can change this to your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body schema
class CompareRequest(BaseModel):
    origin: str
    destination: str
    month: str

# Get coordinates using Open-Meteo geocoding API
def get_coords(place):
    res = requests.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": place})
    results = res.json().get("results")
    if not results:
        return None
    return results[0]["latitude"], results[0]["longitude"]

# Fetch historical temperature data
def get_weather_data(lat, lon, month_str):
    return requests.get("https://archive-api.open-meteo.com/v1/archive", params={
        "latitude": lat,
        "longitude": lon,
        "start_date": f"2023-{month_str}-01",
        "end_date": f"2023-{month_str}-28",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }).json()

# Main route: compare climate
@app.post("/compare")
def compare(req: CompareRequest):
    print("🔍 Request received:", req.dict())

    # Convert month name to number
    try:
        month_number = datetime.strptime(req.month, "%B").month
        month_str = str(month_number).zfill(2)
    except ValueError as e:
        print("❌ Invalid month:", e)
        return {"error": "Invalid month format. Use full name like 'July'."}

    origin_coords = get_coords(req.origin)
    dest_coords = get_coords(req.destination)

    if not origin_coords or not dest_coords:
        print("❌ Geocoding failed")
        return {"error": "Could not find coordinates for one or both locations."}

    try:
        origin_data = get_weather_data(*origin_coords, month_str)
        destination_data = get_weather_data(*dest_coords, month_str)
        print("✅ Weather data fetched")
    except Exception as e:
        print("❌ Weather data error:", e)
        return {"error": f"Failed to fetch weather data: {str(e)}"}

    try:
        gpt_prompt = f"""
Compare the climate between {req.origin} and {req.destination} in {req.month} using the data below.

{req.origin} max temps: {origin_data['daily'].get('temperature_2m_max', [])[:5]}
{req.destination} max temps: {destination_data['daily'].get('temperature_2m_max', [])[:5]}

Summarize the heat and comfort differences in plain English.
"""
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a helpful weather assistant."},
                {"role": "user", "content": gpt_prompt}
            ]
        )
        summary = gpt_response["choices"][0]["message"]["content"]
        print("✅ GPT response complete")
    except Exception as e:
        print("❌ GPT error:", e)
        return {"error": f"OpenAI API error: {str(e)}"}

    return {
        "summary": summary,
        "origin_data": origin_data,
        "destination_data": destination_data
    }
