from pydantic import BaseModel

class HostBase(BaseModel):
    name: str
    email: str
    phone_number: str

class HostCreate(HostBase):
    pass

class HostSchema(HostBase):
    id: int

    class Config:
        orm_mode = True