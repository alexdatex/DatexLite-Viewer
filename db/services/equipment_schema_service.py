from sqlalchemy.orm import Session

from ..database import _models


class EquipmentSchemaService:
    @staticmethod
    def get_schemas(db: Session, equipment_id: int):
        model = _models['EquipmentSchema']
        return db.query(model).filter(model.equipment_id == equipment_id,
                                      model.is_deleted == False).all()

    @staticmethod
    def get_schema(db: Session, schema_id: int):
        model = _models['EquipmentSchema']
        return db.query(model).filter(model.id == schema_id).first()
