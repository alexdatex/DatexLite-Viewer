from db import ComponentService, Equipment


class EquipmentController:
    def __init__(self, db_session):
        self.db = db_session
        self.component_service = ComponentService(db_session)

    def get_equipment(self, equipment_id):
        return self.component_service.get_component(equipment_id)

    def get_all_equipment(self, filters=None):
        return self.component_service.get_components(filters)

    def add_equipment(self, data):
        equipment = Equipment(**data)
        self.db.add(equipment)
        self.db.commit()
        return equipment

    def update_equipment(self, equipment_id, data):
        equipment = self.get_equipment(equipment_id)
        if equipment:
            for key, value in data.items():
                setattr(equipment, key, value)
            self.db.commit()
            return True
        return False

    def delete_equipment(self, equipment_id):
        equipment = self.get_equipment(equipment_id)
        if equipment:
            self.db.delete(equipment)
            self.db.commit()
            return True
        return False
