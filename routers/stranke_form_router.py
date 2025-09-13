from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database_focal import SessionLocal, FastapiStranke
from sqlalchemy.orm import Session
from random import randint

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/stranke_form", response_class=HTMLResponse)
def show_stranka_form(request: Request):
    return templates.TemplateResponse("ustvari_stanko.html", {"request": request})


@router.post("/stranke_form", response_class=HTMLResponse)
def handle_stranka_form(
    request: Request,
    firstname: str = Form(...),
    lastname: str = Form(...),
    address: str = Form(...),
    db: Session = Depends(get_db),
):
    stranka_id = randint(1, 999999)
    new_stranka = FastapiStranke(
        stranka_id=stranka_id, firstname=firstname, lastname=lastname, address=address
    )
    db.add(new_stranka)
    db.commit()
    db.refresh(new_stranka)

    result = {
        "message": "Stranka uspešno dodana!",
        "stranka_id": stranka_id,
        "firstname": firstname,
        "lastname": lastname,
        "address": address,
    }
    return templates.TemplateResponse(
        "ustvari_stanko.html", {"request": request, "result": result}
    )


@router.get("/seznam_strank", response_class=HTMLResponse)
def seznam_strank(request: Request):
    db = SessionLocal()
    stranke = db.query(FastapiStranke).all()
    db.close()
    return templates.TemplateResponse(
        "seznam_strank.html", {"request": request, "stranke": stranke}
    )
