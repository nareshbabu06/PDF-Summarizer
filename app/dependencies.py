from fastapi import Query,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.exceptions import PDFNotFoundError
from app.models import PDF


def pagination_params(limit: int = Query(10, gt=0, le=100), offset: int = Query(0, ge=0)):
    return {"limit": limit, "offset": offset}

def verify_pdf_exists(pdf_id:int,db: Session = Depends(get_db)) -> PDF:
    db_pdf = crud.get_pdf(db, pdf_id)

    if db_pdf is None:
        raise PDFNotFoundError(pdf_id)

    return db_pdf