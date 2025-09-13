from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database_focal import SessionLocal, FastapiGeneriraniRacuni
from schemas.racun_schema import RacunCreate, RacunUpdate, RacunOut

router = APIRouter(prefix="/racuni", tags=["Računi"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create
@router.post("/", response_model=RacunOut)
def create_racun(racun: RacunCreate, db: Session = Depends(get_db)):
    new_racun = FastapiGeneriraniRacuni(**racun.dict())
    db.add(new_racun)
    db.commit()
    db.refresh(new_racun)
    return new_racun


# Read all
@router.get("/", response_model=list[RacunOut])
def read_all_racuni(db: Session = Depends(get_db)):
    return db.query(FastapiGeneriraniRacuni).all()


# Read one
@router.get("/{racun_id}", response_model=RacunOut)
def read_racun(racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(FastapiGeneriraniRacuni).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")
    return racun


# Update
@router.put("/{racun_id}", response_model=RacunOut)
def update_racun(racun_id: int, update: RacunUpdate, db: Session = Depends(get_db)):
    racun = db.query(FastapiGeneriraniRacuni).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")
    racun.koncni_znesek = update.koncni_znesek
    db.commit()
    db.refresh(racun)
    return racun


# Delete
@router.delete("/{racun_id}")
def delete_racun(racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(FastapiGeneriraniRacuni).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")
    db.delete(racun)
    db.commit()
    return {"message": f"Račun {racun_id} deleted"}
