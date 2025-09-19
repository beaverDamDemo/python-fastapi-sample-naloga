from sqlalchemy import Column, Integer, Float, ForeignKey
from models.base import Base


class Racun(Base):
    __tablename__ = "fastapi_racuni"

    id = Column(Integer, primary_key=True, index=True)
    stranka_id = Column(
        Integer,
        ForeignKey("fastapi_stranke.stranka_id", ondelete="CASCADE"),
        nullable=False,
    )
    koncni_znesek = Column(Float, nullable=False)
