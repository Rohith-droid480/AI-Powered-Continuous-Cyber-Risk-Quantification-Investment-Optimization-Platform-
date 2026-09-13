import pytest
from sqlalchemy import create_engine

from app.schemas.models import (
    ParsedVulnerability,
    EnrichedVulnerability,
    EnrichmentStatus,
)
from app.enrichment.db import init_db, CVETable
from app.enrichment.seed_cves import seed_database
from app.enrichment.enrichment import (
    lookup_cve,
    enrich_vulnerability,
    enrich_vulnerabilities,
)


@pytest.fixture(scope="module")
def test_db_engine():
    """
    Creates an isolated in-memory SQLite database engine for testing,
    ensuring deterministic and fast test execution.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    init_db(engine)
    seed_database(engine=engine)
    return engine


def test_enrich_known_cve_hand_computed(test_db_engine):
    """
    Test 1 (Type A Correctness):
    Pass a known CVE (CVE-2021-44228 - Log4Shell).
    Assert output is EnrichmentStatus.FULL, is_kev=True, cvss_score=10.0, and epss_score=0.97.
    """
    parsed = ParsedVulnerability(
        cve_id="CVE-2021-44228",
        plugin_id="156014",
        plugin_name="Apache Log4j Remote Code Execution",
        host="192.168.1.10",
        port=443,
        protocol="tcp",
        severity=4,
        description="Apache Log4j2 JNDI RCE",
    )

    enriched = enrich_vulnerability(parsed, engine=test_db_engine)

    assert isinstance(enriched, EnrichedVulnerability)
    assert enriched.cve_id == "CVE-2021-44228"
    assert enriched.enrichment_status == EnrichmentStatus.FULL
    assert enriched.is_kev is True
    assert enriched.cvss_score == 10.0
    assert enriched.epss_score == 0.97
    assert enriched.host == "192.168.1.10"
    assert enriched.port == 443
    assert enriched.protocol == "tcp"
    assert enriched.severity == 4


def test_enrich_unknown_cve_strict_fallback(test_db_engine):
    """
    Test 2 (Type A Correctness - Strict Fallback Rule):
    Pass an unknown CVE (CVE-9999-0000).
    Assert output is EnrichmentStatus.PARTIAL, epss_score=0.001, is_kev=False, and cvss_score=0.0.
    """
    parsed = ParsedVulnerability(
        cve_id="CVE-9999-0000",
        plugin_id="999999",
        plugin_name="Unrecognized Novel Vulnerability",
        host="10.0.0.99",
        port=8080,
        protocol="tcp",
        severity=3,
        description="Novel vulnerability not present in local CVE database",
    )

    enriched = enrich_vulnerability(parsed, engine=test_db_engine)

    assert isinstance(enriched, EnrichedVulnerability)
    assert enriched.cve_id == "CVE-9999-0000"
    assert enriched.enrichment_status == EnrichmentStatus.PARTIAL
    assert enriched.is_kev is False
    assert enriched.cvss_score == 0.0
    assert enriched.epss_score == 0.001
    assert enriched.host == "10.0.0.99"
    assert enriched.port == 8080
    assert enriched.severity == 3


def test_enrich_additional_sample_cves(test_db_engine):
    """
    Tests additional seeded CVEs matching Layer 1 test scan data:
    - CVE-2021-41773: CVSS=7.5, EPSS=0.80, KEV=True, FULL
    - CVE-2023-38606: CVSS=7.8, EPSS=0.10, KEV=False, FULL
    """
    vuln_apache = ParsedVulnerability(
        cve_id="CVE-2021-41773",
        plugin_id="153583",
        plugin_name="Apache Path Traversal",
        host="192.168.1.10",
        port=80,
        protocol="tcp",
        severity=3,
    )
    enriched_apache = enrich_vulnerability(vuln_apache, engine=test_db_engine)
    assert enriched_apache.enrichment_status == EnrichmentStatus.FULL
    assert enriched_apache.cvss_score == 7.5
    assert enriched_apache.epss_score == 0.80
    assert enriched_apache.is_kev is True

    vuln_apple = ParsedVulnerability(
        cve_id="CVE-2023-38606",
        plugin_id="178901",
        plugin_name="Apple WebKit / Kernel State Modification",
        host="10.0.0.15",
        port=443,
        protocol="tcp",
        severity=3,
    )
    enriched_apple = enrich_vulnerability(vuln_apple, engine=test_db_engine)
    assert enriched_apple.enrichment_status == EnrichmentStatus.FULL
    assert enriched_apple.cvss_score == 7.8
    assert enriched_apple.epss_score == 0.10
    assert enriched_apple.is_kev is False


def test_batch_enrichment(test_db_engine):
    """
    Tests batch enrichment function on a mixed list of known and unknown vulnerabilities.
    """
    vulns = [
        ParsedVulnerability(
            cve_id="CVE-2021-44228",
            plugin_id="1",
            plugin_name="Log4j",
            host="host1",
            port=443,
            protocol="tcp",
            severity=4,
        ),
        ParsedVulnerability(
            cve_id="CVE-UNKNOWN-1234",
            plugin_id="2",
            plugin_name="Unknown",
            host="host2",
            port=80,
            protocol="tcp",
            severity=2,
        ),
    ]

    results = enrich_vulnerabilities(vulns, engine=test_db_engine)
    assert len(results) == 2

    # First is known
    assert results[0].cve_id == "CVE-2021-44228"
    assert results[0].enrichment_status == EnrichmentStatus.FULL
    assert results[0].cvss_score == 10.0
    assert results[0].epss_score == 0.97
    assert results[0].is_kev is True

    # Second is unknown fallback
    assert results[1].cve_id == "CVE-UNKNOWN-1234"
    assert results[1].enrichment_status == EnrichmentStatus.PARTIAL
    assert results[1].cvss_score == 0.0
    assert results[1].epss_score == 0.001
    assert results[1].is_kev is False


def test_seed_database_idempotency(test_db_engine):
    """
    Verifies that running seed_database multiple times is idempotent
    and does not create duplicate entries or fail.
    """
    count1 = seed_database(engine=test_db_engine)
    assert count1 >= 5

    count2 = seed_database(engine=test_db_engine)
    assert count2 == count1
