import sys
import logging
from typing import List, Dict, Any, Optional

from app.enrichment.db import (
    CVETable,
    init_db,
    get_engine,
    get_db_session,
    create_db_engine,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Pre-seeded dictionary matching Layer 1 test and sample scan data
# Strictly offline - DO NOT connect to live external APIs
SEED_CVES: List[Dict[str, Any]] = [
    {
        "cve_id": "CVE-2021-44228",
        "cvss_score": 10.0,
        "epss_score": 0.97,
        "is_kev": True,
        "description": "Apache Log4j2 JNDI remote code execution vulnerability (Log4Shell).",
    },
    {
        "cve_id": "CVE-2021-41773",
        "cvss_score": 7.5,
        "epss_score": 0.80,
        "is_kev": True,
        "description": "Apache HTTP Server 2.4.49 path traversal and file disclosure vulnerability.",
    },
    {
        "cve_id": "CVE-2023-38606",
        "cvss_score": 7.8,
        "epss_score": 0.10,
        "is_kev": False,
        "description": "Apple WebKit and Kernel sensitive state modification vulnerability.",
    },
    {
        "cve_id": "CVE-2020-1472",
        "cvss_score": 10.0,
        "epss_score": 0.95,
        "is_kev": True,
        "description": "Microsoft Netlogon elevation of privilege vulnerability (Zerologon).",
    },
    {
        "cve_id": "CVE-2017-5638",
        "cvss_score": 10.0,
        "epss_score": 0.92,
        "is_kev": True,
        "description": "Apache Struts 2 Jakarta Multipart parser remote code execution vulnerability.",
    },
    {
        "cve_id": "CVE-2008-5161",
        "cvss_score": 2.6,
        "epss_score": 0.02,
        "is_kev": False,
        "description": "SSH Server CBC Mode Ciphers plaintext recovery vulnerability.",
    },
]


def seed_database(
    engine=None,
    cve_records: Optional[List[Dict[str, Any]]] = None,
) -> int:
    """
    Seeds the local database `cves` table with baseline vulnerability metrics.
    Ensures the table exists, upserts all records, and commits.
    
    Returns:
        int: Number of records seeded/updated.
    """
    eng = engine or get_engine()
    init_db(eng)

    records = cve_records if cve_records is not None else SEED_CVES
    seeded_count = 0

    with get_db_session(eng) as session:
        for item in records:
            cve_id = item["cve_id"].strip().upper()
            existing = session.query(CVETable).filter(CVETable.cve_id == cve_id).first()
            if existing:
                existing.cvss_score = float(item["cvss_score"])
                existing.epss_score = float(item["epss_score"])
                existing.is_kev = bool(item["is_kev"])
                existing.description = item.get("description")
            else:
                new_record = CVETable(
                    cve_id=cve_id,
                    cvss_score=float(item["cvss_score"]),
                    epss_score=float(item["epss_score"]),
                    is_kev=bool(item["is_kev"]),
                    description=item.get("description"),
                )
                session.add(new_record)
            seeded_count += 1

    logger.info("Successfully seeded %d CVE records into the local database.", seeded_count)
    return seeded_count


if __name__ == "__main__":
    db_url = sys.argv[1] if len(sys.argv) > 1 else None
    eng = create_db_engine(db_url) if db_url else get_engine()
    count = seed_database(engine=eng)
    print(f"Database seeding completed. {count} CVE records available in local store.")
