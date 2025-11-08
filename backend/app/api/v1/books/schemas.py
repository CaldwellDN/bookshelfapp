from pydantic import BaseModel
from typing import Optional

class BookMetadataUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None

class BookData(BaseModel):
    id: str
    title: str
    author: Optional[str] = None
    file_type: str
    user_id: int

class BookUploadResponse(BaseModel):
    bookData: BookData
    message: str

class BookResponse(BaseModel):
    id: str
    title: str
    author: Optional[str]
    file_type: str
    user_id: int

    class Config:
        from_attributes = True  # This allows Pydantic to read from SQLAlchemy model instances