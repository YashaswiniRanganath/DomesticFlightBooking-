from flask import Flask, request, jsonify
from database import SessionLocal, engine
from models import Base, RoomModel
from schemas import RoomCreate, RoomSchema
from sqlalchemy.orm import Session
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})  # Allow frontend origin
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route('/rooms', methods=['GET'])
def get_rooms():
    db: Session = next(get_db())
    homestay_id = request.args.get('homestay_id')
    if homestay_id:
        rooms = db.query(RoomModel).filter(RoomModel.homestay_id == int(homestay_id)).all()
    else:
        rooms = db.query(RoomModel).all()
    return jsonify([RoomSchema.from_orm(r).dict() for r in rooms])

@app.route('/rooms/<int:id>', methods=['GET'])
def get_room(id):
    db: Session = next(get_db())
    room = db.query(RoomModel).filter(RoomModel.id == id).first()
    if not room:
        return jsonify({"error": "Room not found"}), 404
    return jsonify(RoomSchema.from_orm(room).dict())

@app.route('/rooms', methods=['POST'])
def create_room():
    db: Session = next(get_db())
    data = request.get_json()
    room_data = RoomCreate(**data)
    room = RoomModel(**room_data.dict())
    db.add(room)
    db.commit()
    db.refresh(room)
    return jsonify(RoomSchema.from_orm(room).dict()), 201

@app.route('/rooms/<int:id>', methods=['PUT'])
def update_room(id):
    db: Session = next(get_db())
    room = db.query(RoomModel).filter(RoomModel.id == id).first()
    if not room:
        return jsonify({"error": "Room not found"}), 404
    data = request.get_json()
    for key, value in data.items():
        if key != 'availability':
            setattr(room, key, value)
        else:
            current = room.availability or {}
            current.update(value)
            room.availability = current
    db.commit()
    return jsonify(RoomSchema.from_orm(room).dict())

@app.route('/rooms/<int:id>', methods=['DELETE'])
def delete_room(id):
    db: Session = next(get_db())
    room = db.query(RoomModel).filter(RoomModel.id == id).first()
    if not room:
        return jsonify({"error": "Room not found"}), 404
    db.delete(room)
    db.commit()
    return jsonify({"message": "Room deleted"}), 200

@app.route('/rooms/<int:id>/availability', methods=['GET'])
def get_availability(id):
    db: Session = next(get_db())
    room = db.query(RoomModel).filter(RoomModel.id == id).first()
    if not room:
        return jsonify({"error": "Room not found"}), 404
    return jsonify(room.availability or {})

@app.route('/rooms/<int:id>/set_availability', methods=['POST'])
def set_availability(id):
    db: Session = next(get_db())
    room = db.query(RoomModel).filter(RoomModel.id == id).first()
    if not room:
        return jsonify({"error": "Room not found"}), 404
    data = request.get_json()
    dates = data.get('dates', [])
    status = data.get('status')
    if not dates or not status:
        return jsonify({"error": "Missing dates or status"}), 400
    availability = room.availability or {}
    for date in dates:
        availability[date] = status
    room.availability = availability
    db.commit()
    return jsonify({"message": "Availability updated"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)