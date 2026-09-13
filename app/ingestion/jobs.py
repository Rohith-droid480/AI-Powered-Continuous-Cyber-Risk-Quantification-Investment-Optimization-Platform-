import uuid
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from app.schemas.models import (
    JobStatusEnum,
    JobStatus,
    ParsedVulnerability,
    EnrichedVulnerability,
)
from app.ingestion.parser import parse_nessus_xml, IngestionError
from app.enrichment.enrichment import enrich_vulnerability
from app.enrichment.db import get_db_session

logger = logging.getLogger(__name__)


@dataclass
class JobRecord:
    job_id: str
    status: JobStatusEnum
    message: Optional[str] = None
    enriched_vulnerabilities: List[EnrichedVulnerability] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def parsed_vulnerabilities(self) -> List[EnrichedVulnerability]:
        """Backward-compatible alias returning the in-memory vulnerabilities list."""
        return self.enriched_vulnerabilities

    @parsed_vulnerabilities.setter
    def parsed_vulnerabilities(self, val: List[EnrichedVulnerability]) -> None:
        self.enriched_vulnerabilities = val

    def to_job_status(self) -> JobStatus:
        return JobStatus(
            job_id=self.job_id,
            status=self.status,
            message=self.message,
        )


class JobManager:
    """
    Thread-safe in-memory job state manager for asynchronous scan ingestion and enrichment.
    """

    def __init__(self) -> None:
        self._jobs: Dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def create_job(
        self,
        job_id: Optional[str] = None,
        initial_status: JobStatusEnum = JobStatusEnum.PROCESSING,
        message: Optional[str] = None,
    ) -> str:
        """Creates and stores a new job with initial status."""
        jid = job_id or f"job_{uuid.uuid4().hex[:12]}"
        msg = message or "Scan file received; background ingestion and enrichment in progress."
        record = JobRecord(
            job_id=jid,
            status=initial_status,
            message=msg,
        )
        with self._lock:
            self._jobs[jid] = record
        return jid

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        """Retrieves a job record by job_id."""
        with self._lock:
            return self._jobs.get(job_id)

    def update_job(
        self,
        job_id: str,
        status: JobStatusEnum,
        message: Optional[str] = None,
        vulnerabilities: Optional[List[EnrichedVulnerability]] = None,
    ) -> Optional[JobRecord]:
        """Updates the status, message, and enriched vulnerability records of a job."""
        with self._lock:
            record = self._jobs.get(job_id)
            if not record:
                return None
            record.status = status
            if message is not None:
                record.message = message
            if vulnerabilities is not None:
                record.enriched_vulnerabilities = vulnerabilities
            record.updated_at = datetime.now(timezone.utc)
            return record

    def process_scan_job(self, job_id: str, file_bytes: bytes) -> None:
        """
        Background task worker that executes Nessus parsing, opens a managed database
        session, enriches vulnerabilities, and transitions job state to PARSED.
        
        Fail-soft guarantee:
        - If parsing or enrichment fails: cleanly transitions to INGESTION_FAILED.
        - Closes database sessions safely via context manager.
        - Never leaves sessions dangling or crashes the server.
        """
        try:
            logger.info("Starting background ingestion for job %s (%d bytes)", job_id, len(file_bytes))
            parsed_vulns: List[ParsedVulnerability] = parse_nessus_xml(file_bytes)

            # Safely manage database session using context manager
            enriched_vulns: List[EnrichedVulnerability] = []
            with get_db_session() as session:
                for pv in parsed_vulns:
                    ev = enrich_vulnerability(pv, session=session)
                    enriched_vulns.append(ev)

            self.update_job(
                job_id=job_id,
                status=JobStatusEnum.PARSED,
                message=f"Successfully parsed and enriched {len(enriched_vulns)} vulnerabilities from scan.",
                vulnerabilities=enriched_vulns,
            )
            logger.info(
                "Job %s ingestion & enrichment complete: %d vulnerabilities processed",
                job_id,
                len(enriched_vulns),
            )
        except IngestionError as e:
            logger.warning("Ingestion failed cleanly for job %s: %s", job_id, str(e))
            self.update_job(
                job_id=job_id,
                status=JobStatusEnum.INGESTION_FAILED,
                message=f"Ingestion failed: {str(e)}",
                vulnerabilities=[],
            )
        except Exception as e:
            logger.error("Unexpected ingestion failure for job %s: %s", job_id, str(e), exc_info=True)
            self.update_job(
                job_id=job_id,
                status=JobStatusEnum.INGESTION_FAILED,
                message=f"Ingestion failed due to unexpected error: {str(e)}",
                vulnerabilities=[],
            )

    def clear(self) -> None:
        """Clears all jobs (useful for test isolation)."""
        with self._lock:
            self._jobs.clear()


# Global singleton job manager
job_manager = JobManager()
