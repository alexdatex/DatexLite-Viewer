from sqlalchemy import and_
from sqlalchemy.orm import Session

from constants.status_states import StatusStates
from ..database import _models


class ComponentService:

    @staticmethod
    def add_equipment(db: Session, data: dict):
        model = _models['Equipment']
        equipment = model(**data)
        db.add(equipment)
        db.commit()
        return equipment


    @staticmethod
    def get_component(db: Session, equipment_id: int):
        model = _models['Equipment']
        return db.query(model).filter(model.id == equipment_id, model.is_deleted == False).first()

    @staticmethod
    def get_components(db: Session, filters=None):
        model = _models['Equipment']
        if filters:
            conditions = [model.is_deleted == False]
            for field in filters:
                if hasattr(model, field):
                    value = filters[field].get().strip().replace('%', '\\%').replace('_', '\\_')
                    if value:
                        if field == "is_audit_completed":
                            if value != "":
                                conditions.append(
                                    model.is_audit_completed == StatusStates.get_id_by_text(value))
                        else:
                            field = f"{field}_lower"
                            if hasattr(model, field):
                                value = value.lower()
                                conditions.append(getattr(model, field).like(f"%{value}%"))
            query = db.query(model)
            if len(conditions) == 1:
                return query.filter(conditions[0])

            return query.filter(and_(*conditions))
        else:
            return db.query(model).filter(model.is_deleted == False).all()
