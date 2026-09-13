import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.schemas.models import (
    ParsedVulnerability,
    EnrichedVulnerability,
    EnrichmentStatus,
)
from app.enrichment.db import (
    CVETable,
    get_engine,
    get_db_session,
)

logger = logging.getLogger(__name__)


def lookup_cve(
    cve_id: str,
    session: Optional[Session] = None,
    engine=None,
) -> Optional[CVETable]:
    """
    Performs a local database lookup for a single CVE ID.
    Strictly queries local database table `cves` — no external API calls.
    
    Returns:
        CVETable instance if found, None otherwise.
    """
    if not cve_id:
        return None

    normalized_cve = cve_id.strip().upper()

    if session is not None:
        return session.query(CVETable).filter(CVETable.cve_id == normalized_cve).first()

    eng = engine or get_engine()
    with get_db_session(eng) as sess:
        record = sess.query(CVETable).filter(CVETable.cve_id == normalized_cve).first()
        if record:
            sess.expunge(record)
        return record


def enrich_vulnerability(
    vuln: ParsedVulnerability,
    session: Optional[Session] = None,
    engine=None,
) -> EnrichedVulnerability:
    """
    Enriches a single ParsedVulnerability with CVSS base score, EPSS probability,
    and CISA KEV flag from the local database.
    
    Strict Fallback Rule:
    - If cve_id is FOUND in database:
        cvss_score = db.cvss_score
        epss_score = db.epss_score
        is_kev = db.is_kev
        enrichment_status = EnrichmentStatus.FULL
    - If cve_id is NOT FOUND:
        cvss_score = 0.0
        epss_score = 0.001
        is_kev = False
        enrichment_status = EnrichmentStatus.PARTIAL
    """
    record = lookup_cve(vuln.cve_id, session=session, engine=engine)

    if record is not None:
        cvss_score = float(record.cvss_score)
        epss_score = float(record.epss_score)
        is_kev = bool(record.is_kev)
        status = EnrichmentStatus.FULL
    else:
        # Strict fail-soft fallback rule
        cvss_score = 0.0
        epss_score = 0.001
        is_kev = False
        status = EnrichmentStatus.PARTIAL

    return EnrichedVulnerability(
        cve_id=vuln.cve_id,
        plugin_id=vuln.plugin_id,
        plugin_name=vuln.plugin_name,
        host=vuln.host,
        port=vuln.port,
        protocol=vuln.protocol,
        severity=vuln.severity,
        description=vuln.description,
        cvss_score=cvss_score,
        epss_score=epss_score,
        is_kev=is_kev,
        enrichment_status=status,
    )


def enrich_vulnerabilities(
    vulns: List[ParsedVulnerability],
    engine=None,
) -> List[EnrichedVulnerability]:
    """
    Enriches a list of ParsedVulnerability instances in batch using a single DB session.
    """
    if not vulns:
        return []

    eng = engine or get_engine()
    results: List[EnrichedVulnerability] = []

    with get_db_session(eng) as session:
        for vuln in vulns:
            enriched = enrich_vulnerability(vuln, session=session, engine=eng)
            results.append(enriched)

    return results
