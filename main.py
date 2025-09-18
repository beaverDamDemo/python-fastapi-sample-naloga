from fastapi import FastAPI, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from auth.dependencies import require_login
from database_focal import SessionLocal
from models.stranke_model import Stranka
from models.racuni_model import Racun
from routers.racuni_router import router as racuni_router
from routers.stranke_router import router as stranke_router
from routers.dodaj_stranko_router import router as dodaj_stranko_router
from auth.session import login_user, logout_user, VALID_USERNAME, VALID_PASSWORD
import urllib.parse


app = FastAPI()
app.include_router(racuni_router)
app.include_router(dodaj_stranko_router)
app.include_router(stranke_router)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup():
    from models import racuni_model, stranke_model, vhodni_podatki_model
    from models.base import Base
    from database_focal import engine

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def redirect_unauthenticated(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as e:
        if e.status_code == 302 and "Location" in e.headers:
            return RedirectResponse(url=e.headers["Location"])
        raise e


@app.middleware("http")
async def flash_middleware(request: Request, call_next):
    response = await call_next(request)
    flash = request.cookies.get("flash")
    if flash:
        request.state.flash = urllib.parse.unquote(flash)
        response.delete_cookie("flash")
    return response


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        response = RedirectResponse(url="/", status_code=303)
        login_user(response, username)
        return response
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid credentials"}
    )


@app.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    logout_user(response)
    message = urllib.parse.quote("Uspešno ste se odjavili")
    response.set_cookie(key="flash", value=message, max_age=5)
    return response


@app.get("/time")
def get_time(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT now()")).fetchone()
    return {"server_time": result[0]}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ustvari_racun", response_class=HTMLResponse)
def show_form(request: Request, user: str = Depends(require_login)):
    return templates.TemplateResponse("ustvari_racun.html", {"request": request})


@app.get("/dodaj_stranko", response_class=HTMLResponse)
def show_dodaj_stranko(request: Request):
    return templates.TemplateResponse("create_stranka.html", {"request": request})


@app.get("/upravljaj_stranke", response_class=HTMLResponse)
def upravljaj_stranke(request: Request):
    db = SessionLocal()
    stranke = db.query(Stranka).all()
    db.close()
    return templates.TemplateResponse(
        "upravljaj_stranke.html", {"request": request, "stranke": stranke}
    )


@app.get("/upravljaj_racune", response_class=HTMLResponse)
def upravljaj_racune(
    request: Request, db: Session = Depends(get_db), user: str = Depends(require_login)
):
    racuni = db.query(Racun).all()
    return templates.TemplateResponse(
        "upravljaj_racune.html", {"request": request, "racuni": racuni}
    )


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
