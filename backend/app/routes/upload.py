import os

from fastapi import Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.upload import UploadedFile
from app.models.user import User
from app.services.pylint_service import run_pylint
from app.utils.security import get_current_user
from app.services.bandit_service import run_bandit
from app.services.radon_service import run_radon
UPLOAD_DIR = "app/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


async def upload_code_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".py"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Python .py files are allowed"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    uploaded_file = UploadedFile(
        filename=file.filename,
        filepath=file_path,
        uploaded_by=current_user.id
    )

    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    pylint_report = run_pylint(file_path)
    bandit_report = run_bandit(file_path)
    radon_report = run_radon(file_path)

    return {
        "message": "File uploaded and analyzed successfully",
        "id": uploaded_file.id,
        "filename": uploaded_file.filename,
        "filepath": uploaded_file.filepath,
        "uploaded_by": current_user.email,
        "uploaded_at": uploaded_file.uploaded_at,
        "pylint_report": pylint_report,
        "bandit_report": bandit_report,
        "radon_report": radon_report,
    }


async def get_upload_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uploads = (
        db.query(UploadedFile)
        .filter(UploadedFile.uploaded_by == current_user.id)
        .order_by(UploadedFile.uploaded_at.desc())
        .all()
    )

    return uploads