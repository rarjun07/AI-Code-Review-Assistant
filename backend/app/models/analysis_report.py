from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.database import Base


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(
        String,
        nullable=False
    )

    pylint_report = Column(
        JSON,
        nullable=False
    )

    bandit_report = Column(
        JSON,
        nullable=False
    )

    radon_report = Column(
        JSON,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    upload_id = Column(
        Integer,
        ForeignKey("uploaded_files.id"),
        nullable=False
    )

    owner = relationship("User")
    uploaded_file = relationship("UploadedFile")