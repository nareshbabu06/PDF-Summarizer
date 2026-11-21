from webbrowser import get

from fastapi import FastAPI, HTTPException, Query, Depends
from typing import Optional
from app.schemas import PDFCreate, PDFUpdate,PDFResponse, UserCreate, UserResponse, UserWithPDFs
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.exceptions import DuplicatePDFError, PDFNotFoundError, InvalidPDFError, UserNotFoundError, UserAlreadyExistsError
from app.database import engine,get_db
from app.config import get_settings
from app.dependencies import pagination_params, verify_pdf_exists
from sqlalchemy import text
from sqlalchemy.orm import Session
from app import crud
from app.models import PDF

settings = get_settings()

app = FastAPI(
    title = "PDF Summarizer FastAPI",
    description = "A production-ready API for uploading and summarizing PDFs",
    version = "0.1.0"
)


@app.exception_handler(PDFNotFoundError)
def pdf_not_found_exception_handler(request: Request, exc: PDFNotFoundError):
    return JSONResponse(
        status_code = 404,
        content = {
            "error_code": "PDF_NOT_FOUND",
            "message": f"PDF with id {exc.pdf_id} was not found"
        }
    )


@app.exception_handler(InvalidPDFError)
def invalid_pdf_data_exception_handler(request: Request, exc: InvalidPDFError):
    return JSONResponse(
        status_code = 400,
        content = {
            "error_code": "INVALID_PDF_DATA",
            "message": exc.message
        }
    )

@app.exception_handler(UserNotFoundError)
def user_not_found_exception_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code = 404,
        content = {"error_code": "USER_NOT_FOUND", "message": f"User {exc.user_id} not found"}
    )

@app.exception_handler(UserAlreadyExistsError)
def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code = 409,
        content = {"error_code": "USER_ALREADY_EXISTS", "message": f"Email {exc.email} is already registered"}
    )

@app.exception_handler(DuplicatePDFError)
def duplicate_pdf_handler(request: Request, exc: DuplicatePDFError):
    return JSONResponse(
        status_code=409,
        content={
            "error_code": "DUPLICATE_PDF",
            "message": f"You already have a PDF named {exc.filename}",
        },
    )




@app.get("/")
def read_root():
    return {"message": "PDF Summarizer API is running"}


@app.get("/health")
def health_check():
    return {"status": "Ok"}


@app.post("/pdfs", response_model=PDFResponse, status_code=201)
def create_pdf(pdf_in: PDFCreate, db = Depends(get_db)):
    return crud.create_pdf(db, pdf_in)


@app.get("/pdfs", response_model=list[PDFResponse])
def list_pdfs(
    owner_name: Optional[str] = None,
    pagination: dict = Depends(pagination_params),
    db: Session = Depends(get_db),
):
    return crud.list_pdfs(db, pagination["limit"], pagination["offset"],owner_name)

@app.get("/pdfs/{pdf_id}", response_model=PDFResponse)
def get_pdf(pdf_id: int, db: Session = Depends(get_db)):
    return verify_pdf_exists(pdf_id, db)

@app.patch("/pdfs/{pdf_id}", response_model=PDFResponse)
def update_pdf(updates: PDFUpdate,db_pdf: PDF = Depends(verify_pdf_exists),db: Session = Depends(get_db)):
    return crud.update_pdf(db,db_pdf, updates)


@app.delete("/pdfs/{pdf_id}", status_code=204)
def delete_pdf(db_pdf: PDF = Depends(verify_pdf_exists), db: Session = Depends(get_db)):
    crud.delete_pdf(db,db_pdf)


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user_in.email):
        raise UserAlreadyExistsError(user_in.email)
    return crud.create_pdf(db, user_in)

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise UserNotFoundError(user_id)
    return db_user

@app.get("/users/{user_id}/pdfs", response_model=list[PDFResponse])
def get_user_pdfs(user_id: int, db: Session = Depends(get_db)):
    if crud.get_user(db, user_id) is None:
        raise UserNotFoundError(user_id)
    return crud.list_pdfs_for_user(db, user_id)


@app.post("/pdfs", response_model=PDFResponse, status_code=201)
def create_pdf(pdf_in: PDFCreate, db: Session = Depends(get_db)):
    if crud.get_user(db, pdf_in.owner_id) is None:
        raise UserNotFoundError(pdf_in.owner_id)
    return crud.create_pdf(db, pdf_in)


@app.get("/db-check")
def db_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return {"database": "connection failed", "error": str(e)}


@app.get("/config-check")
def config_check():
    return {"debug": settings.debug}


@app.get("/about")
def about():
    return {"Project Name":"PDF Summarizer API","Description": "A producton-ready API for uploading and summarizing PDFs","version":"0.1.0"}


@app.get("/users/{user_id}/with-pdfs", response_model=UserWithPDFs)
def get_user_with_pdfs(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_with_pdfs(db, user_id)
    if db_user is None:
        raise UserNotFoundError(user_id)
    return db_user


@app.get("/users", response_model=list[UserWithPDFs])
def list_users(pagination: dict = Depends(pagination_params), db: Session = Depends(get_db)):
    return crud.list_users_with_pdfs(db, pagination["limit"], pagination["offset"])


@app.get("/stats/pdfs-per-user")
def pdfs_per_user(db: Session = Depends(get_db)):
    rows = crud.get_pdf_count_per_user(db)
    return [{"user_id": r.id, "name": r.name, "pdf_count": r.pdf_count} for r in rows]




