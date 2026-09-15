import React, { useState } from 'react';
import { formatCurrency } from '../../utils/lecTransformation';

export default function FindingsView({ data }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [kevFilter, setKevFilter] = useState(false);
  const [selectedOnlyFilter, setSelectedOnlyFilter] = useState(false);

  const vulns = data?.vulnerabilities || [];
  const selectedCves = data?.optimization_results?.selected_cves || [];
  const perCveRiskMap = (data?.simulation_results?.per_cve_risk || []).reduce((acc, curr) => {
    acc[curr.cve_id] = curr.baseline_eal;
    return acc;
  }, {});

  // Filter vulnerabilities
  const filteredVulns = vulns.filter((item) => {
    const matchesSearch =
      item.cve_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.plugin_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.host.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesSeverity =
      severityFilter === 'ALL'
        ? true
        : severityFilter === 'CRITICAL'
        ? item.cvss_score >= 9.0
        : severityFilter === 'HIGH'
        ? item.cvss_score >= 7.0 && item.cvss_score < 9.0
        : item.cvss_score < 7.0;

    const matchesKev = kevFilter ? item.is_kev === true : true;
    const matchesSelected = selectedOnlyFilter ? selectedCves.includes(item.cve_id) : true;

    return matchesSearch && matchesSeverity && matchesKev && matchesSelected;
  });

  return (
    <div className="findings-view animate-fadeIn">
      {/* Search & Filter Toolbar */}
      <div className="view-card findings-toolbar-card">
        <div className="toolbar-header">
          <h3 className="card-title font-mono">
            <span className="title-icon">🔍</span> Vulnerability & Threat Intelligence Explorer
          </h3>
          <span className="findings-count font-mono">
            Showing {filteredVulns.length} of {vulns.length} Discovered Findings
          </span>
        </div>

        <div className="toolbar-controls-grid">
          {/* Search Input */}
          <div className="search-input-box">
            <span className="search-icon">🔎</span>
            <input
              type="text"
              placeholder="Search CVE ID, Host IP, or Plugin..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="font-mono"
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="clear-btn font-mono">
                ✕
              </button>
            )}
          </div>

          {/* Severity Filters */}
          <div className="filter-group font-mono">
            <span className="filter-label">Severity:</span>
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`filter-chip ${severityFilter === sev ? 'active' : ''}`}
              >
                {sev}
              </button>
            ))}
          </div>

          {/* Toggle Switches */}
          <div className="toggle-group font-mono">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={kevFilter}
                onChange={(e) => setKevFilter(e.target.checked)}
              />
              <span>CISA KEV Only</span>
            </label>

            <label className="toggle-label">
              <input
                type="checkbox"
                checked={selectedOnlyFilter}
                onChange={(e) => setSelectedOnlyFilter(e.target.checked)}
              />
              <span>PuLP Selected Only</span>
            </label>
          </div>
        </div>
      </div>

      {/* Findings Table Card */}
      <div className="view-card findings-table-card">
        <div className="table-responsive">
          <table className="findings-table">
            <thead>
              <tr className="font-mono">
                <th>CVE ID</th>
                <th>Vulnerability Plugin Name</th>
                <th>Host : Port</th>
                <th>CVSS v3</th>
                <th>EPSS Prob</th>
                <th>KEV Flag</th>
                <th>Baseline EAL</th>
                <th>PuLP Decision</th>
              </tr>
            </thead>
            <tbody>
              {filteredVulns.length > 0 ? (
                filteredVulns.map((vuln) => {
                  const isSelected = selectedCves.includes(vuln.cve_id);
                  const ealVal = perCveRiskMap[vuln.cve_id] || 0;
                  return (
                    <tr key={`${vuln.cve_id}-${vuln.host}`}>
                      <td className="font-mono font-bold text-white">{vuln.cve_id}</td>
                      <td className="vuln-name">{vuln.plugin_name}</td>
                      <td className="font-mono host-cell">
                        {vuln.host}:{vuln.port}
                      </td>
                      <td className="font-mono">
                        <span
                          className={`cvss-badge ${
                            vuln.cvss_score >= 9.0
                              ? 'critical'
                              : vuln.cvss_score >= 7.0
                              ? 'high'
                              : 'medium'
                          }`}
                        >
                          {vuln.cvss_score.toFixed(1)}
                        </span>
                      </td>
                      <td className="font-mono">
                        <span className={`epss-tag ${vuln.epss_score > 0.8 ? 'high' : 'medium'}`}>
                          {(vuln.epss_score * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td>
                        {vuln.is_kev ? (
                          <span className="status-badge kev font-mono">CISA KEV</span>
                        ) : (
                          <span className="status-badge normal font-mono">Standard</span>
                        )}
                      </td>
                      <td className="font-mono text-amber">{formatCurrency(ealVal)}</td>
                      <td>
                        {isSelected ? (
                          <span className="status-badge selected font-mono">Selected (Remediate)</span>
                        ) : (
                          <span className="status-badge unselected font-mono">Unselected</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="8" className="empty-table-cell font-mono">
                    No vulnerability findings matched the current filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
