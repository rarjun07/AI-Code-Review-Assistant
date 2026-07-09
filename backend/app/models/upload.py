from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    filepath = Column(String, nullable=False)

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id")
    )

    owner = relationship("User")