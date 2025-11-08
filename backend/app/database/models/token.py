from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    expires_at = Column(Integer, nullable=False)  # Unix timestamp
    revoked = Column(Boolean, default=False)