from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.domains.blood_pressure import models as bp_models  # noqa: F401
    from app.domains.urinary import models as uri_models  # noqa: F401
    from app.domains.weight import models as wt_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate()


def _migrate():
    """Add new columns to existing tables without Alembic."""
    with engine.connect() as conn:
        for stmt in [
            "ALTER TABLE urinary_records ADD COLUMN water_ml INTEGER",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                pass  # column already exists
