from pydantic import BaseModel

class Flight(BaseModel):
    flight_id: str
    airline: str
    source: str
    destination: str
    departure_time: str
    arrival_time: str
    seats: int
