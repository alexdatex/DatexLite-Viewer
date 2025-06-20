from sqlalchemy import Column, Integer, String, Text, Boolean

from db import register_model


@register_model
class Mark:
    __tablename__ = "mark"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    schema_id = Column(Integer, nullable=True, index=True)
    spare_parts = Column(Boolean)
    x = Column(Integer, nullable=False, index=True)
    y = Column(Integer, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, index=True, default=0)

    def __repr__(self):
        return f"<Mark(id={self.id}"
