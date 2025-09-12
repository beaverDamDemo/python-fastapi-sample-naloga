from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from db import SessionLocal

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def read_root(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT now()")).fetchone()
    return {"Current Time": result[0]}


@app.get("/time")
def get_time(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT now()")).fetchone()
    return {"server_time": result[0]}
