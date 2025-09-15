from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database_focal import SessionLocal, FastapiRacuni
from schemas.racun_schema import RacunCreate, RacunUpdate, RacunOut
from fastapi import Request
from database_focal import FastapiStranke
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from weasyprint import HTML
from starlette.requests import Request
import tempfile


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
    new_racun = FastapiRacuni(**racun.dict())
    db.add(new_racun)
    db.commit()
    db.refresh(new_racun)
    return new_racun


# Read all
@router.get("/", response_model=list[RacunOut])
def read_all_racuni(db: Session = Depends(get_db)):
    return db.query(FastapiRacuni).all()


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
    racun = db.query(FastapiRacuni).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")
    return racun


@router.get("/{racun_id}/poglej_racun", response_class=HTMLResponse)
def view_racun(request: Request, racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(FastapiRacuni).get(racun_id)
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
#     racun = db.query(FastapiRacuni).get(racun_id)
#     if not racun:
#         raise HTTPException(status_code=404, detail="Račun not found")
#     racun.koncni_znesek = update.koncni_znesek
#     db.commit()
#     db.refresh(racun)
#     return racun


# @router.get("/{racun_id}/edit", response_class=HTMLResponse)
# def edit_racun_form(request: Request, racun_id: int, db: Session = Depends(get_db)):
#     racun = db.query(FastapiRacuni).get(racun_id)
#     return templates.TemplateResponse(
#         "edit_racun.html", {"request": request, "racun": racun}
#     )


# Delete
# @router.delete("/{racun_id}")
# def delete_racun(racun_id: int, db: Session = Depends(get_db)):
#     racun = db.query(FastapiRacuni).get(racun_id)
#     if not racun:
#         raise HTTPException(status_code=404, detail="Račun not found")
#     db.delete(racun)
#     db.commit()
#     return {"message": f"Račun {racun_id} deleted"}


@router.post("/{racun_id}/delete")
def delete_racun_web(racun_id: int, db: Session = Depends(get_db)):
    print("Deleting racun with ID:", racun_id)
    racun = db.query(FastapiRacuni).get(racun_id)
    if racun:
        db.delete(racun)
        db.commit()
    return RedirectResponse(url="/upravljaj_racune", status_code=303)


@router.get("/{racun_id}/pdf")
def export_racun_pdf(racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(FastapiRacuni).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")

    stranka = db.query(FastapiStranke).filter_by(stranka_id=racun.stranka_id).first()

    # Render the PDF-specific template (no url_for)
    html_content = templates.get_template("poglej_racun_pdf.html").render(
        racun=racun, stranka=stranka
    )

    # Generate PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        HTML(string=html_content, base_url=".").write_pdf(tmp_file.name)
        pdf_path = tmp_file.name

    filename = f"racun_{racun.id}.pdf"
    return FileResponse(pdf_path, media_type="application/pdf", filename=filename)
