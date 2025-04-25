from pydantic import BaseModel

class Booking(BaseModel):
    user_email: str
    flight_id: str
    seats_booked: int
