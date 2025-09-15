from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database_focal import SessionLocal
from models.stranke_model import Stranka
from schemas.stranke_schema import StrankaCreate, StrankaUpdate, StrankaOut

router = APIRouter(prefix="/stranke", tags=["Stranke"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=StrankaOut)
def create_stranka(stranka: StrankaCreate, db: Session = Depends(get_db)):
    new_stranka = Stranka(**stranka.dict())
    db.add(new_stranka)
    db.commit()
    db.refresh(new_stranka)
    return new_stranka


@router.get("/", response_model=list[StrankaOut])
def read_all_stranke(db: Session = Depends(get_db)):
    return db.query(Stranka).all()


@router.get("/{stranka_id}", response_model=StrankaOut)
def read_stranka(stranka_id: int, db: Session = Depends(get_db)):
    stranka = db.query(Stranka).filter_by(stranka_id=stranka_id).first()
    if not stranka:
        raise HTTPException(
            status_code=404, detail="Stranka with ID {stranka_id} not found"
        )
    return stranka


@router.put("/{stranka_id}", response_model=StrankaOut)
def update_stranka(
    stranka_id: int, update: StrankaUpdate, db: Session = Depends(get_db)
):
    stranka = db.query(Stranka).filter_by(stranka_id=stranka_id).first()
    if not stranka:
        raise HTTPException(
            status_code=404, detail="Stranka with ID {stranka_id} not found"
        )
    for key, value in update.dict().items():
        setattr(stranka, key, value)
    db.commit()
    db.refresh(stranka)
    return stranka


@router.delete("/{stranka_id}")
def delete_stranka(stranka_id: int, db: Session = Depends(get_db)):
    stranka = db.query(Stranka).filter_by(stranka_id=stranka_id).first()
    if not stranka:
        raise HTTPException(
            status_code=404, detail="Stranka with ID {stranka_id} not found"
        )
    db.delete(stranka)
    db.commit()
    return {"message": f"Stranka {stranka_id} deleted"}


@router.post("/{stranka_id}/delete")
def delete_stranka_form(stranka_id: int, db: Session = Depends(get_db)):
    stranka = db.query(Stranka).filter_by(stranka_id=stranka_id).first()
    if not stranka:
        raise HTTPException(status_code=404, detail="Stranka not found")
    db.delete(stranka)
    db.commit()
    return RedirectResponse(url="/stranke", status_code=303)
