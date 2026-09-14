import os
import logging
from typing import Optional
from contextlib import contextmanager
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Boolean,
    Text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


class CVETable(Base):
    """
    SQLAlchemy table model for local pre-seeded CVE vulnerability metrics.
    Stores CVSS base scores, EPSS probabilities, and CISA KEV flags.
    """
    __tablename__ = "cves"

    cve_id = Column(String(50), primary_key=True, index=True, nullable=False)
    cvss_score = Column(Float, nullable=False, default=0.0)
    epss_score = Column(Float, nullable=False, default=0.001)
    is_kev = Column(Boolean, nullable=False, default=False)
    description = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<CVETable(cve_id='{self.cve_id}', cvss={self.cvss_score}, epss={self.epss_score}, is_kev={self.is_kev})>"


def get_database_url() -> str:
    """Loads DATABASE_URL from .env or environment with local fallback."""
    load_dotenv()
    return os.getenv("DATABASE_URL", "sqlite:///./cves.db")


def create_db_engine(db_url: Optional[str] = None):
    """
    Creates and validates an engine connected to PostgreSQL or SQLite.
    If the target PostgreSQL server is unreachable, falls back gracefully
    to local SQLite (cves.db) for zero-crash execution.
    """
    target_url = db_url or get_database_url()
    connect_args = {}

    if target_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    try:
        engine = create_engine(target_url, connect_args=connect_args)
        with engine.connect() as conn:
            pass
        return engine
    except Exception as exc:
        logger.warning(
            "Could not connect to target database %s (%s). Falling back to sqlite:///./cves.db",
            target_url,
            exc,
        )
        fallback_url = "sqlite:///./cves.db"
        fallback_engine = create_engine(fallback_url, connect_args={"check_same_thread": False})
        return fallback_engine


_default_engine = None


def get_engine():
    """Returns or initializes the singleton engine."""
    global _default_engine
    if _default_engine is None:
        _default_engine = create_db_engine()
    return _default_engine


def init_db(engine=None) -> None:
    """Initializes the database schema, creating the cves table if not present."""
    eng = engine or get_engine()
    Base.metadata.create_all(bind=eng)


@contextmanager
def get_db_session(engine=None):
    """Context manager for obtaining a managed database session."""
    eng = engine or get_engine()
    session_factory = sessionmaker(bind=eng, autoflush=False, autocommit=False)
    session: Session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
