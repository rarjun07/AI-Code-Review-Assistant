import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.analysis_report import AnalysisReport
from app.models.upload import UploadedFile
from app.models.user import User
from app.services.upload_cleanup_service import cleanup_orphan_uploads


class UploadCleanupServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        User.__table__.create(self.engine)
        UploadedFile.__table__.create(self.engine)
        AnalysisReport.__table__.create(self.engine)
        self.session = sessionmaker(bind=self.engine)()

        self.user = User(
            name="Arjun",
            email="arjun@example.com",
            password_hash="stored-password-hash",
        )
        self.session.add(self.user)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_cleanup_removes_only_orphan_uploads_and_files(self):
        with tempfile.TemporaryDirectory() as directory:
            upload_directory = Path(directory)
            linked_path = upload_directory / "linked.py"
            orphan_path = upload_directory / "orphan.py"
            linked_path.write_text("print('linked')\n", encoding="utf-8")
            orphan_path.write_text("print('orphan')\n", encoding="utf-8")

            linked_upload = UploadedFile(
                filename="linked.py",
                filepath=str(linked_path),
                uploaded_by=self.user.id,
            )
            orphan_upload = UploadedFile(
                filename="orphan.py",
                filepath=str(orphan_path),
                uploaded_by=self.user.id,
            )
            self.session.add_all([linked_upload, orphan_upload])
            self.session.flush()

            report = AnalysisReport(
                filename="linked.py",
                pylint_report={"issues": [], "score": "10.00"},
                bandit_report={"issues": [], "total_issues": 0},
                radon_report={"grades": []},
                user_id=self.user.id,
                upload_id=linked_upload.id,
            )
            self.session.add(report)
            self.session.commit()
            orphan_id = orphan_upload.id

            with patch(
                "app.services.upload_cleanup_service.UPLOAD_DIR",
                upload_directory,
            ):
                result = cleanup_orphan_uploads(self.session)

            self.assertEqual(result["deleted_upload_rows"], 1)
            self.assertEqual(result["deleted_source_files"], 1)
            self.assertEqual(result["deleted_upload_ids"], [orphan_id])
            self.assertIsNone(self.session.get(UploadedFile, orphan_id))
            self.assertIsNotNone(self.session.get(UploadedFile, linked_upload.id))
            self.assertFalse(orphan_path.exists())
            self.assertTrue(linked_path.exists())


if __name__ == "__main__":
    unittest.main()
