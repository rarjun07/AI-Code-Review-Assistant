import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.analysis_report import AnalysisReport
from app.models.upload import UploadedFile
from app.models.user import User
from app.routes.reports import delete_report
from app.routes.upload import get_upload_history


class ReportDeletionTests(unittest.TestCase):
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
        self.other_user = User(
            name="Other User",
            email="other@example.com",
            password_hash="stored-password-hash",
        )
        self.session.add_all([self.user, self.other_user])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def _create_report(self, filepath: str) -> AnalysisReport:
        uploaded_file = UploadedFile(
            filename="main.py",
            filepath=filepath,
            uploaded_by=self.user.id,
        )
        self.session.add(uploaded_file)
        self.session.flush()

        report = AnalysisReport(
            filename="main.py",
            pylint_report={"issues": [], "score": "10.00"},
            bandit_report={"issues": [], "total_issues": 0},
            radon_report={"grades": []},
            ai_review={"status": "completed"},
            documentation_report={"status": "completed"},
            user_id=self.user.id,
            upload_id=uploaded_file.id,
        )
        self.session.add(report)
        self.session.commit()
        self.session.refresh(report)
        return report

    def test_delete_removes_report_upload_record_and_source_file(self):
        with tempfile.TemporaryDirectory() as directory:
            upload_directory = Path(directory)
            source_file = upload_directory / "stored_main.py"
            source_file.write_text("print('hello')\n", encoding="utf-8")
            report = self._create_report(str(source_file))
            report_id = report.id
            upload_id = report.upload_id

            with patch(
                "app.services.upload_cleanup_service.UPLOAD_DIR",
                upload_directory,
            ):
                response = asyncio.run(
                    delete_report(report_id, self.user, self.session)
                )

            self.assertEqual(response["message"], "Report deleted successfully")
            self.assertTrue(response["source_file_deleted"])
            self.assertIsNone(self.session.get(AnalysisReport, report_id))
            self.assertIsNone(self.session.get(UploadedFile, upload_id))
            self.assertFalse(source_file.exists())

    def test_delete_rejects_report_owned_by_another_user(self):
        report = self._create_report("/tmp/stored_main.py")

        with self.assertRaises(HTTPException) as context:
            asyncio.run(
                delete_report(report.id, self.other_user, self.session)
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertIsNotNone(self.session.get(AnalysisReport, report.id))

    def test_upload_history_excludes_orphan_records(self):
        linked_report = self._create_report("/tmp/linked_main.py")
        orphan_upload = UploadedFile(
            filename="orphan.py",
            filepath="/tmp/orphan.py",
            uploaded_by=self.user.id,
        )
        self.session.add(orphan_upload)
        self.session.commit()

        uploads = asyncio.run(get_upload_history(self.user, self.session))

        self.assertEqual([upload.id for upload in uploads], [linked_report.upload_id])


if __name__ == "__main__":
    unittest.main()
