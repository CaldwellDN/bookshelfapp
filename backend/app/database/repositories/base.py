from sqlalchemy.orm import Session
from typing import TypeVar, Generic, List, Optional
from typing import Type

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[T]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session) -> List[T]:
        return db.query(self.model).all()

    def create(self, db: Session, obj: T) -> T:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, id: int, obj_data: dict) -> Optional[T]:
        obj = self.get(db, id)
        if obj:
            for key, value in obj_data.items():
                setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
            return obj
        return None

    def delete(self, db: Session, id: int) -> bool:
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False