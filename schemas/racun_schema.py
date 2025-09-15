from pydantic import BaseModel


class RacunCreate(BaseModel):
    stranka_id: int
    koncni_znesek: float


class RacunOut(BaseModel):
    id: int
    stranka_id: int
    koncni_znesek: float

    class Config:
        orm_mode = True
