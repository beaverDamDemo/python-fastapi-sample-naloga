from sqlalchemy import Column, Integer, Float
from database_focal import Base  # Reuse the shared Base


class Racun(Base):
    __tablename__ = "fastapi_racuni"

    id = Column(Integer, primary_key=True, index=True)
    stranka_id = Column(Integer, nullable=False)
    koncni_znesek = Column(Float, nullable=False)
