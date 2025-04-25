from flask import Flask, request, jsonify
from database import SessionLocal, engine
from models import Base, HomestayModel, Review
from schemas import HomestayCreate, HomestaySchema, ReviewCreate, Review
from sqlalchemy.orm import Session
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})  # Allow frontend origin
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route('/homestays', methods=['GET'])
def get_homestays():
    db: Session = next(get_db())
    host_id = request.args.get('host_id')
    if host_id:
        homestays = db.query(HomestayModel).filter(HomestayModel.host_id == int(host_id)).all()
    else:
        homestays = db.query(HomestayModel).all()
    return jsonify([HomestaySchema.from_orm(h).dict() for h in homestays])

@app.route('/homestays/<int:id>', methods=['GET'])
def get_homestay(id):
    db: Session = next(get_db())
    homestay = db.query(HomestayModel).filter(HomestayModel.id == id).first()
    if not homestay:
        return jsonify({"error": "Homestay not found"}), 404
    return jsonify(HomestaySchema.from_orm(homestay).dict())

@app.route('/homestays', methods=['POST'])
def create_homestay():
    db: Session = next(get_db())
    data = request.get_json()
    homestay_data = HomestayCreate(**data)
    homestay = HomestayModel(**homestay_data.dict())
    db.add(homestay)
    db.commit()
    db.refresh(homestay)
    return jsonify(HomestaySchema.from_orm(homestay).dict()), 201

@app.route('/homestays/<int:id>', methods=['PUT'])
def update_homestay(id):
    db: Session = next(get_db())
    homestay = db.query(HomestayModel).filter(HomestayModel.id == id).first()
    if not homestay:
        return jsonify({"error": "Homestay not found"}), 404
    data = request.get_json()
    for key, value in data.items():
        setattr(homestay, key, value)
    db.commit()
    return jsonify(HomestaySchema.from_orm(homestay).dict())

@app.route('/homestays/<int:id>', methods=['DELETE'])
def delete_homestay(id):
    db: Session = next(get_db())
    homestay = db.query(HomestayModel).filter(HomestayModel.id == id).first()
    if not homestay:
        return jsonify({"error": "Homestay not found"}), 404
    db.delete(homestay)
    db.commit()
    return jsonify({"message": "Homestay deleted"}), 200

@app.route('/homestays/<int:id>/reviews', methods=['GET'])
def get_reviews(id):
    db: Session = next(get_db())
    reviews = db.query(Review).filter(Review.homestay_id == id).all()
    return jsonify([Review.from_orm(r).dict() for r in reviews])

@app.route('/homestays/<int:id>/reviews', methods=['POST'])
def create_review(id):
    db: Session = next(get_db())
    data = request.get_json()
    review_data = ReviewCreate(**data, homestay_id=id)
    review = Review(**review_data.dict())
    db.add(review)
    db.commit()
    db.refresh(review)
    return jsonify(Review.from_orm(review).dict()), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)