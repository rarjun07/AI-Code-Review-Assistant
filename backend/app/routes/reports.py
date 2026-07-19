from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis_report import AnalysisReport
from app.models.user import User
from app.services.report_export_service import (
    build_report_html,
    build_report_markdown,
    build_report_pdf,
)
from app.services.upload_cleanup_service import delete_uploaded_source
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


async def delete_report(
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

    uploaded_file = report.uploaded_file
    uploaded_filepath = uploaded_file.filepath if uploaded_file else None

    try:
        db.delete(report)
        db.flush()

        if uploaded_file:
            remaining_links = (
                db.query(AnalysisReport)
                .filter(AnalysisReport.upload_id == uploaded_file.id)
                .count()
            )

            if remaining_links == 0:
                db.delete(uploaded_file)

        db.commit()
    except Exception:
        db.rollback()
        raise

    source_file_deleted = delete_uploaded_source(uploaded_filepath)

    return {
        "message": "Report deleted successfully",
        "source_file_deleted": source_file_deleted,
    }


async def export_report(
    report_id: int,
    export_format: str,
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

    normalized_format = export_format.lower()
    base_filename = f"ai-code-review-report-{report.id}"

    if normalized_format == "markdown":
        content = build_report_markdown(report)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={base_filename}.md"
            },
        )

    if normalized_format == "html":
        content = build_report_html(report)
        return Response(
            content=content,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename={base_filename}.html"
            },
        )

    if normalized_format == "pdf":
        try:
            content = build_report_pdf(report)
        except ModuleNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="PDF export requires reportlab. Install backend requirements and restart the backend.",
            ) from exc

        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={base_filename}.pdf"
            },
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported export format. Use markdown, html, or pdf.",
    )
