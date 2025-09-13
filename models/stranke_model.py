from sqlalchemy import Column, Integer, String, Identity
from database_focal import Base  # or from .database import Base if modular
from models.stranke_model import FastapiStranke


class FastapiStranke(Base):
    __tablename__ = "fastapi_stranke"

    stranka_id = Column(Integer, Identity(always=True), primary_key=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    address = Column(String, nullable=False)
