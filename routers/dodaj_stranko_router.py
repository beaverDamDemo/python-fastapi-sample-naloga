from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database_focal import SessionLocal
from models.stranke_model import Stranka
from sqlalchemy.orm import Session
from auth.dependencies import require_login

router = APIRouter(dependencies=[Depends(require_login)])
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dodaj_stranko", response_class=HTMLResponse)
def show_dodaj_stranko(request: Request):
    return templates.TemplateResponse("dodaj_stranko.html", {"request": request})


@router.post("/dodaj_stranko", response_class=HTMLResponse)
def handle_dodaj_stranko(
    request: Request,
    firstname: str = Form(...),
    lastname: str = Form(...),
    address: str = Form(...),
    db: Session = Depends(get_db),
):
    new_stranka = Stranka(firstname=firstname, lastname=lastname, address=address)
    db.add(new_stranka)
    db.commit()
    db.refresh(new_stranka)

    result = {
        "message": "Stranka uspešno dodana!",
        "stranka_id": new_stranka.stranka_id,
        "firstname": new_stranka.firstname,
        "lastname": new_stranka.lastname,
        "address": new_stranka.address,
    }
    return templates.TemplateResponse(
        "dodaj_stranko.html", {"request": request, "result": result}
    )


@router.get("/seznam_strank", response_class=HTMLResponse)
def seznam_strank(request: Request):
    db = SessionLocal()
    stranke = db.query(Stranka).all()
    db.close()
    return templates.TemplateResponse(
        "seznam_strank.html", {"request": request, "stranke": stranke}
    )
