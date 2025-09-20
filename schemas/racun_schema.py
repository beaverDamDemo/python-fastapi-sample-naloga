from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RacunCreate(BaseModel):
    stranka_id: int
    koncni_znesek: float


class RacunOut(BaseModel):
    id: int
    stranka_id: int
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    koncni_znesek: float

    class Config:
        orm_mode = True
