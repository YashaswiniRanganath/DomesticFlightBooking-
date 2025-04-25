from fastapi import FastAPI
from models import Booking
from pymongo import MongoClient
import os
import requests


app = FastAPI()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:secret123@mongodb:27017/flight_booking?authSource=admin")

client = MongoClient(MONGO_URI)
db = client["flight_booking"]
booking_collection = db["bookings"]
flight_collection = db["flights"]

def suggest_homestays(destination: str):
    url = "http://homestay_service:5000/homestays"
    # params = {
    #     "location": destination
    # }
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[Homestay Suggestion] Failed to fetch homestays: {e}")
        return []


@app.post("/book")
def book_flight(booking: Booking):
    flight = flight_collection.find_one({"flight_id": booking.flight_id})
    if not flight:
        return {"message": "Flight not found"}

    if flight["seats"] < booking.seats_booked:
        return {"message": "Not enough seats"}

    flight_collection.update_one(
        {"flight_id": booking.flight_id},
        {"$inc": {"seats": -booking.seats_booked}}
    )
    booking_collection.insert_one(booking.dict())

    # ✅ Suggest homestays after successful booking
    destination = flight.get("destination", "")
    suggestions = suggest_homestays(destination)

    return {
        "message": "Flight booked successfully",
        "suggested_homestays": suggestions
    }


@app.get("/bookings")
def get_bookings():
    return {"bookings": list(booking_collection.find({}, {"_id": 0}))}
