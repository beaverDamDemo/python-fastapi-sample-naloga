from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from database_focal import SessionLocal, FastapiRacuni
from routers import racuni_router
from routers.stranke_router import router as stranke_router
from database_focal import FastapiStranke
from routers.dodaj_stranko_router import router as dodaj_stranko_router


app = FastAPI()
app.include_router(racuni_router.router)
app.include_router(dodaj_stranko_router)
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


@app.get("/ustvari_racun", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("ustvari_racun.html", {"request": request})


@app.get("/dodaj_stranko", response_class=HTMLResponse)
def show_dodaj_stranko(request: Request):
    return templates.TemplateResponse("create_stranka.html", {"request": request})


@app.get("/seznam_strank", response_class=HTMLResponse)
def seznam_strank(request: Request):
    db = SessionLocal()
    stranke = db.query(FastapiStranke).all()
    db.close()
    return templates.TemplateResponse(
        "seznam_strank.html", {"request": request, "stranke": stranke}
    )


@app.get("/upravljaj_racune", response_class=HTMLResponse)
def upravljaj_racune(request: Request, db: Session = Depends(get_db)):
    racuni = db.query(FastapiRacuni).all()
    return templates.TemplateResponse(
        "upravljaj_racune.html", {"request": request, "racuni": racuni}
    )


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
