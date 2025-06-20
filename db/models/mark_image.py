from sqlalchemy import Column, Integer, String, LargeBinary, Text, Boolean

from db import register_model


@register_model
class MarkImage:
    __tablename__ = "mark_image"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    data = Column(LargeBinary)
    mark_id = Column(Integer, nullable=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, index=True, default=0)

    def __repr__(self):
        return f"<MarkImage(id={self.id}"
