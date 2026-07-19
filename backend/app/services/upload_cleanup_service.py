from pathlib import Path

from sqlalchemy.orm import Session

from app.models.analysis_report import AnalysisReport
from app.models.upload import UploadedFile

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"


def delete_uploaded_source(filepath: str | None) -> bool:
    if not filepath:
        return False

    upload_root = UPLOAD_DIR.resolve()
    file_path = Path(filepath).resolve()

    if not file_path.is_relative_to(upload_root):
        return False

    existed = file_path.is_file()

    try:
        file_path.unlink(missing_ok=True)
    except OSError:
        return False

    return existed


def cleanup_orphan_uploads(db: Session) -> dict:
    orphan_uploads = (
        db.query(UploadedFile)
        .outerjoin(
            AnalysisReport,
            AnalysisReport.upload_id == UploadedFile.id,
        )
        .filter(AnalysisReport.id.is_(None))
        .order_by(UploadedFile.id)
        .all()
    )
    orphan_ids = [upload.id for upload in orphan_uploads]
    filepaths = [upload.filepath for upload in orphan_uploads]

    try:
        for upload in orphan_uploads:
            db.delete(upload)

        db.commit()
    except Exception:
        db.rollback()
        raise

    deleted_files = sum(
        1 for filepath in filepaths if delete_uploaded_source(filepath)
    )

    return {
        "deleted_upload_rows": len(orphan_ids),
        "deleted_source_files": deleted_files,
        "deleted_upload_ids": orphan_ids,
    }
