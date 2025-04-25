from sqlalchemy import Column, Integer, String, JSON
from database import Base

class RoomModel(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    homestay_id = Column(Integer)
    type = Column(String)
    beds = Column(Integer)
    pricing = Column(Integer)
    availability = Column(JSON)  # e.g., {"2023-12-01": "available", "2023-12-02": "booked"}