from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.exceptions import UserAlreadyExistsError
from app.models import PDF, User
from app.schemas import PDFCreate, PDFUpdate, UserCreate
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

def create_user(db: Session, user_in: UserCreate) -> User:
    db_user = User(**user_in.model_dump())
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError as e:
        db.rollback()
        if isinstance(e.orig, UniqueViolation):
            raise UserAlreadyExistsError(user_in.email) from e
        raise
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id) -> Optional[User]:
    return db.get(User, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    return db.scalars(stmt).first()

def list_pdfs_for_user(db: Session, user_id: int) -> Sequence[PDF]:
    stmt = select(PDF).where(PDF.owner_id == user_id).order_by(PDF.id)
    return db.scalars(stmt).all()


def create_pdf(db: Session, pdf_in: PDFCreate) -> PDF:
    db_pdf = PDF(**pdf_in.model_dump())
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    return db_pdf

def get_pdf(db: Session, pdf_id: int) -> Optional[PDF]:
    return db.get(PDF, pdf_id)


def list_pdfs(db: Session, limit:int, offset:int,owner_name: Optional[str] = None) -> Sequence[PDF]:
    stmt = select(PDF)
    if owner_name is not None:
        stmt = stmt.where(PDF.owner_name == owner_name)
    stmt = stmt.order_by(PDF.id).offset(offset).limit(limit)
    return db.scalars(stmt).all()

def update_pdf(db: Session, db_pdf: PDF, updates: PDFUpdate) -> PDF:
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_pdf, field, value)
    db.commit()
    db.refresh(db_pdf)
    return db_pdf

def delete_pdf(db: Session, db_pdf: PDF) -> None:
    db.delete(db_pdf)
    db.commit()

def get_user_with_pdfs(db: Session, user_id: int) -> Optional[User]:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.pdfs)) 
    )
    return db.scalars(stmt).first()


def list_users_with_pdfs(db: Session, limit: int, offset: int) -> Sequence[User]:
    stmt = (
        select(User)
        .options(selectinload(User.pdfs))
        .order_by(User.id)
        .offset(offset)
        .limit(limit)
    )
    return db.scalars(stmt).all()


def get_pdf_count_per_user(db: Session):
    stmt = (
        select(User.id, User.name, func.count(PDF.id).label("pdf_count"))
        .outerjoin(PDF, PDF.owner_id == User.id)
        .group_by(User.id, User.name)
        .order_by(User.id)
    )
    return db.execute(stmt).all() 
