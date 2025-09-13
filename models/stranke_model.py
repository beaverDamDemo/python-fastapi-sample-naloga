from sqlalchemy import Column, Integer, String
from database_focal import Base  # or from .database import Base if modular
from models.stranke_model import FastapiStranke


class FastapiStranke(Base):
    __tablename__ = "fastapi_stranke"

    id = Column(Integer, primary_key=True, index=True)
    stranka_id = Column(Integer, nullable=False, unique=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    address = Column(String, nullable=False)
