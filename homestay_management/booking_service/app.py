from flask import Flask, request, jsonify
from database import SessionLocal, engine
from models import Base, BookingModel
from schemas import BookingCreate, BookingSchema
from sqlalchemy.orm import Session
import requests
from datetime import datetime, timedelta
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})  # Allow frontend origin
Base.metadata.create_all(bind=engine)

ROOM_SERVICE_URL = "http://room_service:5000"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_dates(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates

@app.route('/bookings', methods=['POST'])
def create_booking():
    db: Session = next(get_db())
    data = request.get_json()
    booking_data = BookingCreate(**data)
    room_id = booking_data.room_id
    start_date = booking_data.start_date.strftime("%Y-%m-%d")
    end_date = booking_data.end_date.strftime("%Y-%m-%d")
    dates = get_dates(start_date, end_date)

    # Check availability
    response = requests.get(f"{ROOM_SERVICE_URL}/rooms/{room_id}/availability")
    if response.status_code != 200:
        return jsonify({"error": "Room not found"}), 404
    availability = response.json()
    for date in dates:
        if availability.get(date) != "available":
            return jsonify({"error": f"Date {date} is not available"}), 400

    # Book the dates
    book_data = {"dates": dates, "status": "booked"}
    response = requests.post(f"{ROOM_SERVICE_URL}/rooms/{room_id}/set_availability", json=book_data)
    if response.status_code != 200:
        return jsonify({"error": "Failed to book dates"}), 500

    # Create booking
    booking = BookingModel(**booking_data.dict())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return jsonify(BookingSchema.from_orm(booking).dict()), 201

@app.route('/bookings/<int:id>', methods=['GET'])
def get_booking(id):
    db: Session = next(get_db())
    booking = db.query(BookingModel).filter(BookingModel.id == id).first()
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    return jsonify(BookingSchema.from_orm(booking).dict())

@app.route('/bookings/<int:id>', methods=['PUT'])
def update_booking(id):
    db: Session = next(get_db())
    booking = db.query(BookingModel).filter(BookingModel.id == id).first()
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    data = request.get_json()
    for key, value in data.items():
        setattr(booking, key, value)
    if data.get('status') == "canceled":
        start_date = booking.start_date.strftime("%Y-%m-%d")
        end_date = booking.end_date.strftime("%Y-%m-%d")
        dates = get_dates(start_date, end_date)
        free_data = {"dates": dates, "status": "available"}
        requests.post(f"{ROOM_SERVICE_URL}/rooms/{booking.room_id}/set_availability", json=free_data)
    db.commit()
    return jsonify(BookingSchema.from_orm(booking).dict())

@app.route('/bookings', methods=['GET'])
def get_bookings():
    db: Session = next(get_db())
    user_id = request.args.get('user_id')
    if user_id:
        bookings = db.query(BookingModel).filter(BookingModel.user_id == int(user_id)).all()
    else:
        bookings = db.query(BookingModel).all()
    return jsonify([BookingSchema.from_orm(b).dict() for b in bookings])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)