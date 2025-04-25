from sqlalchemy import Column, Integer, String, Date
from database import Base

class BookingModel(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer)
    user_id = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String)  # e.g., "confirmed", "canceled"