from sqlalchemy.orm import Session
from typing import Optional
from app.database.models.user import User
from app.database.repositories.base import BaseRepository

class UserRepository:
    def __init__(self):
        self.model = User

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(self.model).filter(self.model.username == username).first()

    def create(self, db: Session, username: str, hashed_password: str) -> User:
        db_user = self.model(username=username, password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(self.model).filter(self.model.id == user_id).first()