from db.services import ComponentService, EquipmentSchemaService, MarkService, MarkImageService
from .database import _models

class DBController:
    def __init__(self, db):
        self.db = db

    def add_equipment(self, data: dict):
        return ComponentService.add_equipment(self.db, data)

    def get_component(self, equipment_id: int):
        return ComponentService.get_component(self.db, equipment_id)

    def get_components(self, filters=None):
        return ComponentService.get_components(self.db, filters)

    def delete_equipment(self, equipment_id: int):
        equipment = self.get_component(equipment_id)
        equipment.is_deleted = True
        self.db.commit()

    def add_schema(self, data: dict):
        model = _models['EquipmentSchema']
        schema = model(**data)
        self.db.add(schema)
        self.db.commit()
        return schema

    def delete_schema(self, schema_id: id):
        schema = self.get_schema(schema_id)
        schema.is_deleted = True
        self.db.commit()

    def get_schemas(self, equipment_id: int):
        return EquipmentSchemaService.get_schemas(self.db, equipment_id)

    def get_schema(self, schema_id: int):
        return EquipmentSchemaService.get_schema(self.db, schema_id)

    def add_mark(self, data: dict):
        model = _models['Mark']
        mark = model(**data)
        self.db.add(mark)
        self.db.commit()
        return mark

    def get_mark(self, mark_id: int):
        return MarkService.get_mark(self.db, mark_id)

    def update_mark(self, mark_id, data):
        mark = self.get_mark(mark_id)
        if mark:
            for key, value in data.items():
                if key != "id":
                    setattr(mark, key, value)
            self.db.commit()


    def delete_mark(self, mark_id: int):
        mark = self.get_mark(mark_id)
        mark.is_deleted = True
        self.db.commit()


    def get_marks(self, schema_id: int):
        return MarkService.get_marks(self.db, schema_id)

    def add_mark_image(self, data: dict):
        model = _models['MarkImage']
        mark_image = model(**data)
        self.db.add(mark_image)
        self.db.commit()
        return mark_image

    def delete_mark_image(self, mark_image_id: int):
        mark_image = self.get_mark_image(mark_image_id)
        mark_image.is_deleted = True
        self.db.commit()

    def get_mark_image(self, mark_image_id: int):
        return MarkImageService.get_mark_image(self.db, mark_image_id)

    def get_mark_images(self, mark_id: int):
        return MarkImageService.get_mark_images(self.db, mark_id)
