from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from database_focal import SessionLocal, FastapiVhodniPodatki, FastapiGeneriraniRacuni
from schemas.racun import RacunCreate, RacunUpdate, RacunOut
from routers import generirani_racuni
from routers.stranke import router as stranke_router
from database_focal import FastapiStranke


app = FastAPI()
app.include_router(generirani_racuni.router)
app.include_router(stranke_router)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/time")
def get_time(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT now()")).fetchone()
    return {"server_time": result[0]}


@app.post("/generiraj_racun/")
def generiraj_racun(stranka_id: int, db: Session = Depends(get_db)):
    # 1. Get all rows for this stranka_id
    rows = (
        db.query(FastapiVhodniPodatki)
        .filter(FastapiVhodniPodatki.stranka_id == stranka_id)
        .all()
    )

    if not rows:
        return {"message": f"No data found for stranka_id {stranka_id}"}

    # 2. Calculate koncni_znesek
    koncni_znesek = 0.0
    for row in rows:
        if row.poraba is not None and row.dinamicne_cene is not None:
            koncni_znesek += row.poraba * row.dinamicne_cene

    # 3. Insert into fastapi_generirani_racuni
    new_racun = FastapiGeneriraniRacuni(
        stranka_id=stranka_id, koncni_znesek=koncni_znesek
    )
    db.add(new_racun)
    db.commit()
    db.refresh(new_racun)

    return {
        "message": "Račun generated successfully",
        "stranka_id": stranka_id,
        "koncni_znesek": koncni_znesek,
    }


@app.get("/generiraj_racun_form", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("generiraj_racun.html", {"request": request})


# Handle form submission
@app.post("/generiraj_racun_form", response_class=HTMLResponse)
def handle_form(
    request: Request, stranka_id: int = Form(...), db: Session = Depends(get_db)
):
    # same logic as your API endpoint
    rows = (
        db.query(FastapiVhodniPodatki)
        .filter(FastapiVhodniPodatki.stranka_id == stranka_id)
        .all()
    )

    if not rows:
        result = {"message": f"No data found for stranka_id {stranka_id}"}
        return templates.TemplateResponse(
            "generiraj_racun.html", {"request": request, "result": result}
        )

    koncni_znesek = sum(
        float(row.poraba) * float(row.dinamicne_cene)
        for row in rows
        if row.poraba is not None and row.dinamicne_cene is not None
    )

    new_racun = FastapiGeneriraniRacuni(
        stranka_id=stranka_id, koncni_znesek=koncni_znesek
    )
    db.add(new_racun)
    db.commit()
    db.refresh(new_racun)

    result = {
        "message": "Račun generated successfully",
        "stranka_id": stranka_id,
        "koncni_znesek": koncni_znesek,
    }
    return templates.TemplateResponse(
        "generiraj_racun.html", {"request": request, "result": result}
    )


@app.get("/stranke_list", response_class=HTMLResponse)
def list_stranke(request: Request):
    db = SessionLocal()
    stranke = db.query(FastapiStranke).all()
    db.close()
    return templates.TemplateResponse(
        "list_stranke.html", {"request": request, "stranke": stranke}
    )


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
