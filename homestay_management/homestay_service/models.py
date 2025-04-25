from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database import Base

class HomestayModel(Base):
    __tablename__ = "homestays"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    description = Column(Text)
    photos = Column(Text)  # Comma-separated URLs or JSON
    amenities = Column(Text)  # Comma-separated list or JSON
    host_id = Column(Integer)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    homestay_id = Column(Integer, ForeignKey("homestays.id"))
    user_id = Column(Integer)
    rating = Column(Integer)
    comment = Column(Text)