from pydantic import BaseModel,ConfigDict, Field, field_validator, ValidationError,EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: str
    created_at: datetime


class FileStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class OwnerInfo(BaseModel):
    name: str
    email: str

class PDFCreate(BaseModel):
    filename: str
    owner_id: int
    pages: int = Field(gt = 0)

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        if not v.lower().endswith(".pdf"):
            raise ValueError("Filename must end with .pdf")
        return v

class PDFUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    filename: Optional[str] = None
    status: Optional[FileStatus] = None

class PDFResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    owner_id: int
    pages: int
    status: FileStatus
    created_at: datetime


class UserWithPDFs(UserResponse):
    pdfs: list[PDFResponse] = []



