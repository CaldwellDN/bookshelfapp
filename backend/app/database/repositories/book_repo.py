from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.models.book import Book
from app.database.repositories.base import BaseRepository

class BookRepository:
    def __init__(self):
        self.model = Book

    def get_by_id(self, db: Session, book_id: str) -> Optional[Book]:
        return db.query(self.model).filter(self.model.id == book_id).first()

    def get_by_user_id(self, db: Session, user_id: int) -> List[Book]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

    def create(self, db: Session, book_data: dict) -> Book:
        db_book = self.model(**book_data)
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book

    def update(self, db: Session, book_id: str, update_data: dict) -> Optional[Book]:
        db_book = self.get_by_id(db, book_id)
        if db_book:
            for key, value in update_data.items():
                setattr(db_book, key, value)
            db.commit()
            db.refresh(db_book)
            return db_book
        return None

    def delete(self, db: Session, book_id: str) -> bool:
        db_book = self.get_by_id(db, book_id)
        if db_book:
            db.delete(db_book)
            db.commit()
            return True
        return False