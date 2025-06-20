from sqlalchemy import Column, Integer, String, Boolean, SmallInteger

from db import register_model


@register_model
class Equipment:
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    korpus = Column(String(50, collation="NOCASE"), nullable=True)
    position = Column(String(50, collation="NOCASE"), nullable=True)
    code = Column(String(50, collation="NOCASE"), nullable=True)
    name = Column(String(100, collation="NOCASE"), nullable=True)
    purpose = Column(String(collation="NOCASE"), nullable=True)
    manufacturer = Column(String(100, collation="NOCASE"), nullable=True)
    type = Column(String(100, collation="NOCASE"), nullable=True)
    serial_number = Column(String(50, collation="NOCASE"), nullable=True)
    production_date = Column(String(50, collation="NOCASE"), nullable=True)
    group_name = Column(String(100, collation="NOCASE"), nullable=True)
    user_id = Column(Integer, nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    is_audit_completed = Column(SmallInteger, default=0, nullable=False, index=True)
    korpus_lower = Column(String(50, collation="NOCASE"), nullable=True)
    position_lower = Column(String(50, collation="NOCASE"), nullable=True)
    code_lower = Column(String(50, collation="NOCASE"), nullable=True)
    name_lower = Column(String(100, collation="NOCASE"), nullable=True)
    purpose_lower = Column(String(collation="NOCASE"), nullable=True)
    manufacturer_lower = Column(String(100, collation="NOCASE"), nullable=True)
    type_lower = Column(String(100, collation="NOCASE"), nullable=True)
    serial_number_lower = Column(String(50, collation="NOCASE"), nullable=True)
    production_date_lower = Column(String(50, collation="NOCASE"), nullable=True)
    group_name_lower = Column(String(100, collation="NOCASE"), nullable=True)

    def __repr__(self):
        return f"<Equipment(id={self.id}"
