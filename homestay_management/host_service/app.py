from flask import Flask, request, jsonify
from database import SessionLocal, engine
from models import Base, HostModel
from schemas import HostCreate, HostSchema
from sqlalchemy.orm import Session
import requests
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})  # Allow frontend origin
Base.metadata.create_all(bind=engine)

HOMESTAY_SERVICE_URL = "http://homestay_service:5000"
ROOM_SERVICE_URL = "http://room_service:5000"
BOOKING_SERVICE_URL = "http://booking_service:5000"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route('/hosts', methods=['POST'])
def create_host():
    db: Session = next(get_db())
    data = request.get_json()
    host_data = HostCreate(**data)
    host = HostModel(**host_data.dict())
    db.add(host)
    db.commit()
    db.refresh(host)
    return jsonify(HostSchema.from_orm(host).dict()), 201

@app.route('/hosts/<int:id>', methods=['GET'])
def get_host(id):
    db: Session = next(get_db())
    host = db.query(HostModel).filter(HostModel.id == id).first()
    if not host:
        return jsonify({"error": "Host not found"}), 404
    return jsonify(HostSchema.from_orm(host).dict())

@app.route('/hosts/<int:id>/homestays', methods=['GET'])
def get_host_homestays(id):
    response = requests.get(f"{HOMESTAY_SERVICE_URL}/homestays?host_id={id}")
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch homestays"}), 500
    return jsonify(response.json())

@app.route('/hosts/<int:id>/homestays', methods=['POST'])
def create_host_homestay(id):
    data = request.get_json()
    data['host_id'] = id
    response = requests.post(f"{HOMESTAY_SERVICE_URL}/homestays", json=data)
    if response.status_code != 201:
        return jsonify({"error": "Failed to create homestay"}), 500
    return jsonify(response.json()), 201

@app.route('/hosts/<int:id>/bookings', methods=['GET'])
def get_host_bookings(id):
    # Get homestays for host
    homestays_resp = requests.get(f"{HOMESTAY_SERVICE_URL}/homestays?host_id={id}")
    if homestays_resp.status_code != 200:
        return jsonify({"error": "Failed to fetch homestays"}), 500
    homestays = homestays_resp.json()
    homestay_ids = [h['id'] for h in homestays]

    # Get rooms for each homestay
    room_ids = []
    for hid in homestay_ids:
        rooms_resp = requests.get(f"{ROOM_SERVICE_URL}/rooms?homestay_id={hid}")
        if rooms_resp.status_code == 200:
            room_ids.extend([r['id'] for r in rooms_resp.json()])

    # Get bookings for all rooms
    bookings = []
    for rid in room_ids:
        bookings_resp = requests.get(f"{BOOKING_SERVICE_URL}/bookings?room_id={rid}")
        if bookings_resp.status_code == 200:
            bookings.extend(bookings_resp.json())
    return jsonify(bookings)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)