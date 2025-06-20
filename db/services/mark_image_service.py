from sqlalchemy.orm import Session

from ..database import _models


class MarkImageService:
    @staticmethod
    def get_mark_image(db: Session, mark_image_id: int):
        model = _models['MarkImage']
        return db.query(model).filter(model.id == mark_image_id).first()

    @staticmethod
    def get_mark_images(db: Session, mark_id: int):
        model = _models['MarkImage']
        return db.query(model).filter(model.mark_id == mark_id, model.is_deleted == False).all()
