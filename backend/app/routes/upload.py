import os
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis_report import AnalysisReport
from app.models.upload import UploadedFile
from app.models.user import User
from app.services.bandit_service import run_bandit
from app.services.documentation_service import generate_documentation
from app.services.openai_service import generate_ai_review
from app.services.pylint_service import run_pylint
from app.services.radon_service import run_radon
from app.services.upload_cleanup_service import delete_uploaded_source
from app.utils.security import get_current_user
from app.utils.validation import validate_python_upload

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


async def upload_code_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_path = None

    try:
        content = await file.read()
        safe_filename = validate_python_upload(file.filename, content)
        stored_filename = f"{uuid4().hex}_{safe_filename}"
        file_path = UPLOAD_DIR / stored_filename

        with file_path.open("wb") as buffer:
            buffer.write(content)

        uploaded_file = UploadedFile(
            filename=safe_filename,
            filepath=str(file_path),
            uploaded_by=current_user.id,
        )

        db.add(uploaded_file)
        db.flush()

        pylint_report = run_pylint(str(file_path), safe_filename)
        bandit_report = run_bandit(str(file_path))
        radon_report = run_radon(str(file_path))
        code = content.decode("utf-8", errors="replace")
        documentation_report = generate_documentation(
            code,
            safe_filename,
        )
        ai_review = generate_ai_review(
            code,
            pylint_report,
            bandit_report,
            radon_report,
        )

        analysis_report = AnalysisReport(
            filename=safe_filename,
            pylint_report=pylint_report,
            bandit_report=bandit_report,
            radon_report=radon_report,
            ai_review=ai_review,
            documentation_report=documentation_report,
            user_id=current_user.id,
            upload_id=uploaded_file.id,
        )

        db.add(analysis_report)
        db.commit()
        db.refresh(uploaded_file)
        db.refresh(analysis_report)

        return {
            "message": "File uploaded and analyzed successfully",
            "report_id": analysis_report.id,
            "id": uploaded_file.id,
            "filename": uploaded_file.filename,
            "uploaded_by": current_user.email,
            "uploaded_at": uploaded_file.uploaded_at,
            "pylint_report": pylint_report,
            "bandit_report": bandit_report,
            "radon_report": radon_report,
            "ai_review": ai_review,
            "documentation_report": documentation_report,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File analysis failed. Please try again.",
        ) from exc

    finally:
        await file.close()
        delete_uploaded_source(str(file_path) if file_path else None)


async def get_upload_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uploads = (
        db.query(UploadedFile)
        .join(
            AnalysisReport,
            AnalysisReport.upload_id == UploadedFile.id,
        )
        .filter(
            UploadedFile.uploaded_by == current_user.id,
            AnalysisReport.user_id == current_user.id,
        )
        .order_by(UploadedFile.uploaded_at.desc())
        .all()
    )

    return uploads
