from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database_focal import SessionLocal, FastapiGeneriraniRacuni
from schemas.racun_schema import RacunCreate, RacunUpdate, RacunOut
from fastapi import Request
from fastapi.responses import HTMLResponse
from database_focal import FastapiStranke
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="/racuni", tags=["Računi"])

templates = Jinja2Templates(directory="templates")


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


@router.get("/isci_stranko", response_class=HTMLResponse)
def search_stranka(request: Request, search_name: str, db: Session = Depends(get_db)):
    results = (
        db.query(FastapiStranke)
        .filter(
            (FastapiStranke.firstname.ilike(f"%{search_name}%"))
            | (FastapiStranke.lastname.ilike(f"%{search_name}%"))
        )
        .all()
    )

    return templates.TemplateResponse(
        "ustvari_racun.html",  # or whatever your template is called
        {"request": request, "search_results": results},
    )


# Read one, it must be defined AFTER isci_stranko
@router.get("/{racun_id}", response_model=RacunOut)
def read_racun(racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(FastapiGeneriraniRacuni).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")
    return racun


@router.get("/{racun_id}/poglej_racun", response_class=HTMLResponse)
def view_racun(request: Request, racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(FastapiGeneriraniRacuni).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")

    # Get linked stranka info
    stranka = db.query(FastapiStranke).filter_by(stranka_id=racun.stranka_id).first()

    return templates.TemplateResponse(
        "poglej_racun.html", {"request": request, "racun": racun, "stranka": stranka}
    )


# Update
# @router.put("/{racun_id}", response_model=RacunOut)
# def update_racun(racun_id: int, update: RacunUpdate, db: Session = Depends(get_db)):
#     racun = db.query(FastapiGeneriraniRacuni).get(racun_id)
#     if not racun:
#         raise HTTPException(status_code=404, detail="Račun not found")
#     racun.koncni_znesek = update.koncni_znesek
#     db.commit()
#     db.refresh(racun)
#     return racun


# @router.get("/{racun_id}/edit", response_class=HTMLResponse)
# def edit_racun_form(request: Request, racun_id: int, db: Session = Depends(get_db)):
#     racun = db.query(FastapiGeneriraniRacuni).get(racun_id)
#     return templates.TemplateResponse(
#         "edit_racun.html", {"request": request, "racun": racun}
#     )


# Delete
# @router.delete("/{racun_id}")
# def delete_racun(racun_id: int, db: Session = Depends(get_db)):
#     racun = db.query(FastapiGeneriraniRacuni).get(racun_id)
#     if not racun:
#         raise HTTPException(status_code=404, detail="Račun not found")
#     db.delete(racun)
#     db.commit()
#     return {"message": f"Račun {racun_id} deleted"}


@router.post("/{racun_id}/delete")
def delete_racun_web(racun_id: int, db: Session = Depends(get_db)):
    print("Deleting racun with ID:", racun_id)
    racun = db.query(FastapiGeneriraniRacuni).get(racun_id)
    if racun:
        db.delete(racun)
        db.commit()
    return RedirectResponse(url="/upravljaj_racune", status_code=303)
