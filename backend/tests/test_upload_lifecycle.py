import asyncio
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from starlette.datastructures import Headers, UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.analysis_report import AnalysisReport
from app.models.upload import UploadedFile
from app.models.user import User
from app.routes.upload import upload_code_file


class UploadLifecycleTests(unittest.TestCase):
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

    def test_successful_analysis_keeps_report_but_removes_source(self):
        uploaded = UploadFile(
            file=io.BytesIO(b"print('hello')\n"),
            filename="main.py",
            headers=Headers({"content-type": "text/x-python"}),
        )

        with tempfile.TemporaryDirectory() as directory:
            upload_directory = Path(directory)

            with (
                patch("app.routes.upload.UPLOAD_DIR", upload_directory),
                patch(
                    "app.services.upload_cleanup_service.UPLOAD_DIR",
                    upload_directory,
                ),
                patch(
                    "app.routes.upload.run_pylint",
                    return_value={"issues": [], "score": "10.00"},
                ),
                patch(
                    "app.routes.upload.run_bandit",
                    return_value={"issues": [], "total_issues": 0},
                ),
                patch(
                    "app.routes.upload.run_radon",
                    return_value={"grades": []},
                ),
                patch(
                    "app.routes.upload.generate_documentation",
                    return_value={"status": "completed"},
                ),
                patch(
                    "app.routes.upload.generate_ai_review",
                    return_value={"status": "completed"},
                ),
            ):
                response = asyncio.run(
                    upload_code_file(uploaded, self.user, self.session)
                )

            self.assertEqual(response["ai_review"]["status"], "completed")
            self.assertEqual(self.session.query(UploadedFile).count(), 1)
            self.assertEqual(self.session.query(AnalysisReport).count(), 1)
            self.assertEqual(list(upload_directory.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
