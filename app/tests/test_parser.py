import pytest
from pathlib import Path
from app.ingestion.parser import parse_nessus_xml, NessusParsingError, IngestionError

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "sample-data"


def test_hand_computed_single_finding():
    """
    Unit test with a hand-computable expected output.
    Given a minimal Nessus XML with exactly 1 host and 1 finding:
      Host: 10.1.1.50
      Port: 443
      Protocol: tcp
      Severity: 4
      PluginID: 99901
      PluginName: Hand Computed Test Vulnerability
      CVE: CVE-2024-0001
      Description: Verification finding for Layer 1 ingestion.

    Expected hand-computed results:
      Count: 1
      All 8 fields match exact known constants.
    """
    raw_xml = """<?xml version="1.0" ?>
<NessusClientData_v2>
  <Report name="Hand-Computed Test Scan">
    <ReportHost name="10.1.1.50">
      <ReportItem port="443" protocol="tcp" severity="4" pluginID="99901" pluginName="Hand Computed Test Vulnerability">
        <description>Verification finding for Layer 1 ingestion.</description>
        <cve>CVE-2024-0001</cve>
      </ReportItem>
    </ReportHost>
  </Report>
</NessusClientData_v2>
"""
    vulns = parse_nessus_xml(raw_xml)

    assert len(vulns) == 1
    v = vulns[0]
    assert v.cve_id == "CVE-2024-0001"
    assert v.plugin_id == "99901"
    assert v.plugin_name == "Hand Computed Test Vulnerability"
    assert v.host == "10.1.1.50"
    assert v.port == 443
    assert v.protocol == "tcp"
    assert v.severity == 4
    assert v.description == "Verification finding for Layer 1 ingestion."


def test_enterprise_perimeter_scan_hand_computed():
    """
    Verifies enterprise_perimeter_scan.nessus against exact hand-computable counts:
    - 2 hosts: 192.168.1.10 (3 findings) and 192.168.1.20 (2 findings)
    - Total findings: 5
    - Severity 4 count: 3 (CVE-2021-44228, CVE-2017-5638, CVE-2020-1472)
    - Severity 3 count: 1 (CVE-2021-41773)
    - Severity 1 count: 1 (CVE-2008-5161)
    """
    scan_file = SAMPLE_DATA_DIR / "enterprise_perimeter_scan.nessus"
    assert scan_file.exists(), f"Missing test file {scan_file}"

    with open(scan_file, "r", encoding="utf-8") as f:
        content = f.read()

    vulns = parse_nessus_xml(content)
    assert len(vulns) == 5

    cve_set = {v.cve_id for v in vulns}
    expected_cves = {
        "CVE-2021-44228",
        "CVE-2021-41773",
        "CVE-2017-5638",
        "CVE-2020-1472",
        "CVE-2008-5161",
    }
    assert cve_set == expected_cves

    sev_4_vulns = [v for v in vulns if v.severity == 4]
    sev_3_vulns = [v for v in vulns if v.severity == 3]
    sev_1_vulns = [v for v in vulns if v.severity == 1]
    assert len(sev_4_vulns) == 3
    assert len(sev_3_vulns) == 1
    assert len(sev_1_vulns) == 1

    # Check host mapping
    host10_vulns = [v for v in vulns if v.host == "192.168.1.10"]
    host20_vulns = [v for v in vulns if v.host == "192.168.1.20"]
    assert len(host10_vulns) == 3
    assert len(host20_vulns) == 2


def test_internal_services_scan_hand_computed():
    """
    Verifies internal_services_scan.nessus against exact hand-computable counts:
    - 1 host: 10.0.0.15
    - Total findings: 3 (CVE-2023-38606, CVE-2022-3602, CVE-2023-4863)
    """
    scan_file = SAMPLE_DATA_DIR / "internal_services_scan.nessus"
    assert scan_file.exists(), f"Missing test file {scan_file}"

    with open(scan_file, "rb") as f:
        content = f.read()

    vulns = parse_nessus_xml(content)
    assert len(vulns) == 3

    cve_list = [v.cve_id for v in vulns]
    assert cve_list == ["CVE-2023-38606", "CVE-2022-3602", "CVE-2023-4863"]
    assert all(v.host == "10.0.0.15" for v in vulns)


def test_malformed_xml_triggers_nessus_parsing_error():
    """
    Fail-soft test: Verifies that parsing a deliberately corrupted .nessus file
    raises NessusParsingError cleanly, without unhandled exceptions or crashing.
    """
    scan_file = SAMPLE_DATA_DIR / "malformed_corrupt.nessus"
    assert scan_file.exists(), f"Missing test file {scan_file}"

    with open(scan_file, "rb") as f:
        content = f.read()

    with pytest.raises(NessusParsingError) as exc_info:
        parse_nessus_xml(content)

    assert "Failed to parse XML syntax" in str(exc_info.value)
    assert issubclass(NessusParsingError, IngestionError)


def test_empty_or_whitespace_scan():
    """Verifies that empty content raises NessusParsingError."""
    with pytest.raises(NessusParsingError) as exc_info:
        parse_nessus_xml("")
    assert "empty" in str(exc_info.value).lower()

    with pytest.raises(NessusParsingError) as exc_info:
        parse_nessus_xml("   \n\t  ")
    assert "whitespace" in str(exc_info.value).lower()


def test_non_nessus_xml():
    """Verifies that arbitrary XML missing NessusClientData_v2 root raises NessusParsingError."""
    arbitrary_xml = "<Document><Item name='test'/></Document>"
    with pytest.raises(NessusParsingError) as exc_info:
        parse_nessus_xml(arbitrary_xml)
    assert "Expected <NessusClientData_v2>" in str(exc_info.value)
