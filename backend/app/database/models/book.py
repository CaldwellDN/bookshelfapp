from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    file_type = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)  # This should reference user.id, but keeping as int for now