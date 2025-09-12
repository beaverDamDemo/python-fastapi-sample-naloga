import os
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FastapiGeneriraniRacuni(Base):
    __tablename__ = "fastapi_generirani_racuni"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_name = Column(String, nullable=False)
    user_surname = Column(String, nullable=False)
    koncni_znesek = Column(Float, nullable=False)


# --- Create tables automatically ---
Base.metadata.create_all(bind=engine)
