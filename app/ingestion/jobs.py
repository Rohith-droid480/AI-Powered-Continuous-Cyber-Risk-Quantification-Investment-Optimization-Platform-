import uuid
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from app.schemas.models import JobStatusEnum, JobStatus, ParsedVulnerability
from app.ingestion.parser import parse_nessus_xml, IngestionError

logger = logging.getLogger(__name__)


@dataclass
class JobRecord:
    job_id: str
    status: JobStatusEnum
    message: Optional[str] = None
    parsed_vulnerabilities: List[ParsedVulnerability] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_job_status(self) -> JobStatus:
        return JobStatus(
            job_id=self.job_id,
            status=self.status,
            message=self.message,
        )


class JobManager:
    """
    Thread-safe in-memory job state manager for asynchronous scan ingestion.
    """

    def __init__(self) -> None:
        self._jobs: Dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def create_job(self, job_id: Optional[str] = None, initial_status: JobStatusEnum = JobStatusEnum.PROCESSING, message: Optional[str] = None) -> str:
        """Creates and stores a new job with PROCESSING status."""
        jid = job_id or f"job_{uuid.uuid4().hex[:12]}"
        msg = message or "Scan file received; background ingestion in progress."
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
        vulnerabilities: Optional[List[ParsedVulnerability]] = None,
    ) -> Optional[JobRecord]:
        """Updates the status, message, and parsed data of a job."""
        with self._lock:
            record = self._jobs.get(job_id)
            if not record:
                return None
            record.status = status
            if message is not None:
                record.message = message
            if vulnerabilities is not None:
                record.parsed_vulnerabilities = vulnerabilities
            record.updated_at = datetime.now(timezone.utc)
            return record

    def process_scan_job(self, job_id: str, file_bytes: bytes) -> None:
        """
        Background task worker that executes Nessus parsing and transitions job state.
        
        Fail-soft guarantee:
        - If parsing succeeds: updates status to PARSED and attaches parsed records.
        - If parsing fails (malformed XML, corrupt file, invalid schema):
          cleanly updates status to INGESTION_FAILED with descriptive message.
          Never raises an unhandled exception or crashes the server.
        """
        try:
            logger.info("Starting background ingestion for job %s (%d bytes)", job_id, len(file_bytes))
            vulnerabilities = parse_nessus_xml(file_bytes)
            self.update_job(
                job_id=job_id,
                status=JobStatusEnum.PARSED,
                message=f"Successfully parsed {len(vulnerabilities)} vulnerabilities from scan.",
                vulnerabilities=vulnerabilities,
            )
            logger.info("Job %s ingestion complete: %d vulnerabilities parsed", job_id, len(vulnerabilities))
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
