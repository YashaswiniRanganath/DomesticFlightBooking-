from pydantic import BaseModel
from datetime import date

class BookingBase(BaseModel):
    room_id: int
    user_id: int
    start_date: date
    end_date: date
    status: str

class BookingCreate(BookingBase):
    pass

class BookingSchema(BookingBase):
    id: int

    class Config:
        orm_mode = True