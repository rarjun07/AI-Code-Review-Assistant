from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis_report import AnalysisReport
from app.models.user import User
from app.utils.security import get_current_user


async def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reports = (
        db.query(AnalysisReport)
        .filter(AnalysisReport.user_id == current_user.id)
        .order_by(AnalysisReport.created_at.desc())
        .all()
    )

    return reports


async def get_report_by_id(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = (
        db.query(AnalysisReport)
        .filter(
            AnalysisReport.id == report_id,
            AnalysisReport.user_id == current_user.id,
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return report