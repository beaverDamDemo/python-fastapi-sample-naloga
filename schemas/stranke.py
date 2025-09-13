from pydantic import BaseModel


class StrankaCreate(BaseModel):
    firstname: str
    lastname: str
    address: str


class StrankaUpdate(BaseModel):
    firstname: str
    lastname: str
    address: str


class StrankaOut(StrankaCreate):
    id: int
    stranka_id: int
    firstname: str
    lastname: str
    address: str

    class Config:
        orm_mode = True
