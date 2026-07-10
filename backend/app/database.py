from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def ensure_analysis_report_columns():
    inspector = inspect(engine)

    if not inspector.has_table("analysis_reports"):
        return

    columns = {
        column["name"]
        for column in inspector.get_columns("analysis_reports")
    }

    missing_columns = []

    if "ai_review" not in columns:
        missing_columns.append(
            "ALTER TABLE analysis_reports ADD COLUMN ai_review JSON"
        )

    if "documentation_report" not in columns:
        missing_columns.append(
            "ALTER TABLE analysis_reports ADD COLUMN documentation_report JSON"
        )

    with engine.begin() as connection:
        for statement in missing_columns:
            connection.execute(text(statement))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
