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