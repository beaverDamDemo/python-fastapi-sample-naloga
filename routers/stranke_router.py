from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from auth.dependencies import require_login
from database_focal import SessionLocal
from models.stranke_model import Stranka
from schemas.stranke_schema import StrankaCreate, StrankaOut, StrankaUpdate

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/stranke", tags=["Stranke"], dependencies=[Depends(require_login)]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{stranka_id}/uredi", response_class=HTMLResponse)
def uredi_stranko_form(
    stranka_id: int, request: Request, db: Session = Depends(get_db)
):
    print(f"Edit route hit for stranka_id={stranka_id}")
    stranka = db.query(Stranka).get(stranka_id)
    if not stranka:
        raise HTTPException(status_code=404, detail="Stranka not found")
    return templates.TemplateResponse(
        "uredi_stranko.html", {"request": request, "stranka": stranka}
    )


@router.post("/{stranka_id}/uredi")
def uredi_stranko_submit(
    stranka_id: int,
    firstname: str = Form(...),
    lastname: str = Form(...),
    address: str = Form(...),
    db: Session = Depends(get_db),
):
    stranka = db.query(Stranka).get(stranka_id)
    stranka.firstname = firstname
    stranka.lastname = lastname
    stranka.address = address
    db.commit()
    return RedirectResponse(url="/upravljaj_stranke", status_code=303)


@router.post("/{stranka_id}/delete")
def delete_stranka_form(stranka_id: int, db: Session = Depends(get_db)):
    stranka = db.query(Stranka).filter_by(stranka_id=stranka_id).first()
    if not stranka:
        raise HTTPException(status_code=404, detail="Stranka not found")
    db.delete(stranka)
    db.commit()
    return RedirectResponse(url="/upravljaj_stranke", status_code=303)


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
