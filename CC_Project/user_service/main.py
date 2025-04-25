from fastapi import FastAPI
from models import User
from pymongo import MongoClient
import os


app = FastAPI()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:secret123@mongodb:27017/flight_booking?authSource=admin")

client = MongoClient(MONGO_URI)
db = client["flight_booking"]
user_collection = db["users"]

@app.post("/register")
def register_user(user: User):
    if user_collection.find_one({"email": user.email}):
        return {"message": "User already exists"}
    user_collection.insert_one(user.dict())
    return {"message": "User registered successfully"}

@app.post("/login")
def login_user(user: User):
    stored = user_collection.find_one({"email": user.email})
    if stored and stored["password"] == user.password:
        return {"message": "Login successful"}
    return {"message": "Invalid credentials"}
