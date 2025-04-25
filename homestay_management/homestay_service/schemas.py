from pydantic import BaseModel

class HomestayBase(BaseModel):
    name: str
    location: str
    description: str
    photos: str
    amenities: str
    host_id: int

class HomestayCreate(HomestayBase):
    pass

class HomestaySchema(HomestayBase):
    id: int

    class Config:
        orm_mode = True

class ReviewBase(BaseModel):
    homestay_id: int
    user_id: int
    rating: int
    comment: str

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int

    class Config:
        orm_mode = True