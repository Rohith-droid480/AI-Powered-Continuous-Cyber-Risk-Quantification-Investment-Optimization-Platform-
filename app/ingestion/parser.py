import re
from typing import List, Union, Optional
import xml.etree.ElementTree as ET

try:
    import defusedxml.ElementTree as SafeET
except ImportError:
    SafeET = ET

from app.schemas.models import ParsedVulnerability


class IngestionError(Exception):
    """Base exception for scan ingestion failures."""
    pass


class NessusParsingError(IngestionError):
    """Raised when Nessus XML content is invalid, malformed, or unparseable."""
    pass


def parse_nessus_xml(xml_data: Union[str, bytes]) -> List[ParsedVulnerability]:
    """
    Parses Nessus Client Data v2 XML content and extracts vulnerability findings.
    
    Each finding is mapped directly to the ParsedVulnerability Pydantic schema:
    - cve_id: str (e.g. CVE-2021-44228)
    - plugin_id: str
    - plugin_name: str
    - host: str
    - port: int
    - protocol: str
    - severity: int
    - description: Optional[str]

    Raises:
        NessusParsingError: If XML is malformed, empty, or lacks valid Nessus structure.
    """
    if not xml_data:
        raise NessusParsingError("Uploaded scan content is empty.")

    if isinstance(xml_data, str):
        xml_bytes = xml_data.encode("utf-8")
    elif isinstance(xml_data, bytes):
        xml_bytes = xml_data
    else:
        raise NessusParsingError(f"Unsupported XML data type: {type(xml_data).__name__}")

    if not xml_bytes.strip():
        raise NessusParsingError("Uploaded scan content contains only whitespace.")

    try:
        root = SafeET.fromstring(xml_bytes)
    except Exception as e:
        raise NessusParsingError(f"Failed to parse XML syntax: {str(e)}") from e

    # Validate Nessus XML structure
    tag_name = root.tag
    if "NessusClientData" not in tag_name and "NessusClientData_v2" not in tag_name:
        raise NessusParsingError(
            f"Invalid root tag <{tag_name}>. Expected <NessusClientData_v2>."
        )

    report_elem = root.find("Report")
    if report_elem is None:
        raise NessusParsingError("Nessus scan does not contain a <Report> element.")

    vulnerabilities: List[ParsedVulnerability] = []

    # Iterate through each ReportHost in the report
    for host_elem in report_elem.findall("ReportHost"):
        host_name = host_elem.get("name", "").strip()
        
        # Check host-ip in HostProperties as fallback/refinement if host_name is generic
        host_props = host_elem.find("HostProperties")
        if host_props is not None:
            for tag in host_props.findall("tag"):
                if tag.get("name") == "host-ip" and tag.text:
                    host_name = tag.text.strip()
                    break

        if not host_name:
            host_name = "unknown-host"

        # Iterate through each ReportItem on this host
        for item in host_elem.findall("ReportItem"):
            plugin_id = item.get("pluginID", "").strip()
            plugin_name = item.get("pluginName", "").strip()
            
            raw_port = item.get("port", "0")
            try:
                port = int(raw_port)
            except ValueError:
                port = 0

            protocol = item.get("protocol", "tcp").strip().lower()
            
            raw_severity = item.get("severity", "0")
            try:
                severity = int(raw_severity)
            except ValueError:
                severity = 0

            # Extract description
            desc_elem = item.find("description")
            description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else None

            # Collect CVE IDs for this finding
            cve_list: List[str] = []
            for cve_elem in item.findall("cve"):
                if cve_elem.text:
                    cve_val = cve_elem.text.strip().upper()
                    if cve_val and cve_val not in cve_list:
                        cve_list.append(cve_val)

            # Map each CVE found in this item to a ParsedVulnerability
            for cve_id in cve_list:
                vuln = ParsedVulnerability(
                    cve_id=cve_id,
                    plugin_id=plugin_id,
                    plugin_name=plugin_name,
                    host=host_name,
                    port=port,
                    protocol=protocol,
                    severity=severity,
                    description=description,
                )
                vulnerabilities.append(vuln)

    return vulnerabilities
