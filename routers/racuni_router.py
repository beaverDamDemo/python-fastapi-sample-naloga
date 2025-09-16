import tempfile

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from weasyprint import HTML

from auth.dependencies import require_login
from database_focal import SessionLocal
from models.racuni_model import Racun
from models.stranke_model import Stranka
from models.vhodni_podatki_model import VhodniPodatki
from schemas.racun_schema import RacunCreate, RacunOut


router = APIRouter(
    prefix="/racuni", tags=["Računi"], dependencies=[Depends(require_login)]
)

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
    new_racun = Racun(**racun.dict())
    db.add(new_racun)
    db.commit()
    db.refresh(new_racun)
    return new_racun


# Read all
@router.get("/", response_model=list[RacunOut])
def read_all_racuni(db: Session = Depends(get_db)):
    return db.query(Racun).all()


@router.get("/isci_stranko", response_class=HTMLResponse)
def search_stranka(request: Request, search_name: str, db: Session = Depends(get_db)):
    results = (
        db.query(Stranka)
        .filter(
            (Stranka.firstname.ilike(f"%{search_name}%"))
            | (Stranka.lastname.ilike(f"%{search_name}%"))
        )
        .all()
    )

    return templates.TemplateResponse(
        "ustvari_racun.html",  # or whatever your template is called
        {"request": request, "search_results": results},
    )


@router.post("/ustvari_racun", response_class=HTMLResponse)
def handle_form(
    request: Request, stranka_id: int = Form(...), db: Session = Depends(get_db)
):
    rows = db.query(VhodniPodatki).filter(VhodniPodatki.stranka_id == stranka_id).all()

    if not rows:
        result = {"message": f"No data found for stranka_id {stranka_id}"}
        return templates.TemplateResponse(
            "ustvari_racun.html", {"request": request, "result": result}
        )

    koncni_znesek = sum(
        float(row.poraba) * float(row.dinamicne_cene)
        for row in rows
        if row.poraba is not None and row.dinamicne_cene is not None
    )

    new_racun = Racun(stranka_id=stranka_id, koncni_znesek=koncni_znesek)
    db.add(new_racun)
    db.commit()
    db.refresh(new_racun)

    result = {
        "message": "Račun ustvarjen uspešno",
        "stranka_id": stranka_id,
        "koncni_znesek": koncni_znesek,
    }
    return templates.TemplateResponse(
        "ustvari_racun.html", {"request": request, "result": result}
    )


# Read one, it must be defined AFTER isci_stranko
@router.get("/{racun_id}", response_model=RacunOut)
def read_racun(racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(Racun).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")
    return racun


@router.get("/{racun_id}/poglej_racun", response_class=HTMLResponse)
def view_racun(request: Request, racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(Racun).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")

    # Get linked stranka info
    stranka = db.query(Stranka).filter_by(stranka_id=racun.stranka_id).first()

    return templates.TemplateResponse(
        "poglej_racun.html", {"request": request, "racun": racun, "stranka": stranka}
    )


@router.post("/{racun_id}/delete")
def delete_racun_web(racun_id: int, db: Session = Depends(get_db)):
    print("Deleting racun with ID:", racun_id)
    racun = db.query(Racun).get(racun_id)
    if racun:
        db.delete(racun)
        db.commit()
    return RedirectResponse(url="/upravljaj_racune", status_code=303)


@router.get("/{racun_id}/pdf")
def export_racun_pdf(racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(Racun).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")

    stranka = db.query(Stranka).filter_by(stranka_id=racun.stranka_id).first()

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
