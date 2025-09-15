from pydantic import BaseModel, Field
from typing import Optional


class StrankaCreate(BaseModel):
    firstname: str = Field(..., min_length=2, max_length=50)
    lastname: str = Field(..., min_length=2, max_length=50)
    address: str = Field(..., min_length=5, max_length=100)


class StrankaUpdate(BaseModel):
    firstname: Optional[str] = Field(None, min_length=2)
    lastname: Optional[str] = Field(None, min_length=2)
    address: Optional[str] = Field(None, min_length=5)


class StrankaOut(StrankaCreate):
    stranka_id: int

    class Config:
        orm_mode = True
