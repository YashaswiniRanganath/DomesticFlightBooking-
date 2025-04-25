from fastapi import FastAPI
from models import Flight
from pymongo import MongoClient
import requests
import os


app = FastAPI()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:secret123@mongodb:27017/flight_booking?authSource=admin")

client = MongoClient(MONGO_URI)
db = client["flight_booking"]
user_collection = db["flights"]
flight_collection = db["flights"]

def add_homestays(destination: str):
    url = "http://homestay_service:5000/homestays"
    payload = {
        "name": f"{destination} Homestay",
        "location": destination,
        "description": f"A lovely homestay in {destination}",
        "photos": "http://example.com/photo.jpg",
        "amenities": "wifi,ac,parking",
        "host_id": 1
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[Homestay Suggestion] Failed to create homestay: {e}")
        return []


@app.post("/add-flight")
def add_flight(flight: Flight):
    if flight_collection.find_one({"flight_id": flight.flight_id}):
        return {"message": "Flight already exists"}
    
    destination = flight.destination
    suggestions = add_homestays(destination)

    flight_collection.insert_one(flight.dict())
    return {"message": "Flight added successfully", "info":suggestions}

@app.get("/flights")
def get_flights():
    flights = list(flight_collection.find({}, {'_id': 0}))
    return {"flights": flights}
