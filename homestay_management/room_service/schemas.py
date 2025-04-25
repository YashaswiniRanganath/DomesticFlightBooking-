from pydantic import BaseModel

class RoomBase(BaseModel):
    homestay_id: int
    type: str
    beds: int
    pricing: int
    availability: dict

class RoomCreate(RoomBase):
    pass

class RoomSchema(RoomBase):
    id: int

    class Config:
        orm_mode = True