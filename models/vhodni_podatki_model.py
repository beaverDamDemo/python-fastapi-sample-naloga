from models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Float,
    TIMESTAMP,
    ForeignKey,
)


class VhodniPodatki(Base):
    __tablename__ = "fastapi_vhodni_podatki"

    id = Column(Integer, primary_key=True, index=True)
    casovna_znacka = Column(TIMESTAMP(timezone=True))
    poraba = Column(Float)
    dinamicne_cene = Column(Float)
    stranka_id = Column(
        Integer, ForeignKey("fastapi_stranke.stranka_id", ondelete="CASCADE")
    )
