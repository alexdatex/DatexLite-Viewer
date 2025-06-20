from sqlalchemy.orm import Session

from ..database import _models


class MarkService:
    @staticmethod
    def get_mark(db: Session, mark_id: int):
        model = _models['Mark']
        return db.query(model).filter(model.id == mark_id).first()

    @staticmethod
    def get_marks(db: Session, schema_id: int):
        model = _models['Mark']
        return db.query(model).filter(model.schema_id == schema_id, model.is_deleted == False).all()
