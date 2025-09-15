import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    TIMESTAMP,
    Identity,
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
import models
from models.base import Base
from models import stranke_model, racuni_model

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FastapiVhodniPodatki(Base):
    __tablename__ = "fastapi_vhodni_podatki"

    id = Column(Integer, primary_key=True, index=True)
    casovna_znacka = Column(TIMESTAMP(timezone=True))
    poraba = Column(Float)
    dinamicne_cene = Column(Float)
    stranka_id = Column(Integer)  # Foreign key to stranke.id


class FastapiRacuni(Base):
    __tablename__ = "fastapi_racuni"

    id = Column(Integer, primary_key=True, index=True)
    stranka_id = Column(Integer, nullable=False)
    koncni_znesek = Column(Float, nullable=False)


# --- Create tables automatically ---
Base.metadata.create_all(bind=engine)
