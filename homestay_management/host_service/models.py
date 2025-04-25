from sqlalchemy import Column, Integer, String
from database import Base

class HostModel(Base):
    __tablename__ = "hosts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phone_number = Column(String)