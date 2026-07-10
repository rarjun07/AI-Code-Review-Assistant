import os

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
from app.utils.security import get_current_user

UPLOAD_DIR = "app/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


async def upload_code_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".py"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Python .py files are allowed",
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        content = await file.read()

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        uploaded_file = UploadedFile(
            filename=file.filename,
            filepath=file_path,
            uploaded_by=current_user.id,
        )

        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)

        pylint_report = run_pylint(file_path)
        bandit_report = run_bandit(file_path)
        radon_report = run_radon(file_path)
        code = content.decode("utf-8", errors="replace")
        documentation_report = generate_documentation(
            code,
            file.filename,
        )
        ai_review = generate_ai_review(
            code,
            pylint_report,
            bandit_report,
            radon_report,
        )

        analysis_report = AnalysisReport(
            filename=file.filename,
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
        db.refresh(analysis_report)

        return {
            "message": "File uploaded and analyzed successfully",
            "report_id": analysis_report.id,
            "id": uploaded_file.id,
            "filename": uploaded_file.filename,
            "filepath": uploaded_file.filepath,
            "uploaded_by": current_user.email,
            "uploaded_at": uploaded_file.uploaded_at,
            "pylint_report": pylint_report,
            "bandit_report": bandit_report,
            "radon_report": radon_report,
            "ai_review": ai_review,
            "documentation_report": documentation_report,
        }

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File analysis failed: {str(exc)}",
        ) from exc

    finally:
        await file.close()


async def get_upload_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uploads = (
        db.query(UploadedFile)
        .filter(UploadedFile.uploaded_by == current_user.id)
        .order_by(UploadedFile.uploaded_at.desc())
        .all()
    )

    return uploads
