from sqlalchemy.orm import Session
from typing import Optional
from app.database.models.token import RefreshToken
from app.database.repositories.base import BaseRepository

class TokenRepository:
    def __init__(self):
        self.model = RefreshToken

    def get_by_jti(self, db: Session, jti: str) -> Optional[RefreshToken]:
        return db.query(self.model).filter(self.model.jti == jti).first()

    def get_by_username(self, db: Session, username: str) -> list[RefreshToken]:
        return db.query(self.model).filter(self.model.username == username).all()

    def create(self, db: Session, jti: str, username: str, expires_at: int) -> RefreshToken:
        db_token = self.model(jti=jti, username=username, expires_at=expires_at, revoked=False)
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token

    def update(self, db: Session, jti: str, update_data: dict) -> Optional[RefreshToken]:
        db_token = self.get_by_jti(db, jti)
        if db_token:
            for key, value in update_data.items():
                setattr(db_token, key, value)
            db.commit()
            db.refresh(db_token)
            return db_token
        return None

    def revoke_token(self, db: Session, jti: str) -> bool:
        db_token = self.get_by_jti(db, jti)
        if db_token:
            db_token.revoked = True
            db.commit()
            db.refresh(db_token)
            return True
        return False

    def is_token_active(self, db: Session, jti: str) -> bool:
        db_token = self.get_by_jti(db, jti)
        if db_token and not db_token.revoked:
            from datetime import datetime
            return datetime.now().timestamp() < db_token.expires_at
        return False