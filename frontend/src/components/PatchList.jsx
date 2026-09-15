import React from 'react';
import { formatCurrency } from '../utils/lecTransformation';

function getCvssCategory(score) {
  if (score >= 9.0) return { label: 'Critical (40h)', cls: 'critical' };
  if (score >= 7.0) return { label: 'High (16h)', cls: 'high' };
  if (score >= 4.0) return { label: 'Medium (8h)', cls: 'medium' };
  return { label: 'Low (4h)', cls: 'low' };
}

function calculateCost(cvssScore) {
  if (cvssScore >= 9.0) return 40 * 2000;
  if (cvssScore >= 7.0) return 16 * 2000;
  if (cvssScore >= 4.0) return 8 * 2000;
  return 4 * 2000;
}

export default function PatchList({
  vulnerabilities = [],
  simulationResults = null,
  optimizationResults = null,
}) {
  const selectedCvesSet = new Set(optimizationResults?.selected_cves || []);
  const deltaEalMap = optimizationResults?.delta_eal_per_cve || {};
  const perCveSummaries = simulationResults?.per_cve_risk || [];

  // Group per-CVE risk metrics
  const cveMap = new Map();

  perCveSummaries.forEach((item) => {
    cveMap.set(item.cve_id, {
      cve_id: item.cve_id,
      cvss: 7.5,
      deltaEal: item.baseline_eal,
      cost: 32000,
    });
  });

  vulnerabilities.forEach((vuln) => {
    const existing = cveMap.get(vuln.cve_id) || {};
    const cvss = vuln.cvss_score ?? existing.cvss ?? 0.0;
    const cost = calculateCost(cvss);
    const deltaEal = existing.deltaEal ?? (vuln.epss_score ? vuln.epss_score * 357000000 : 0);

    cveMap.set(vuln.cve_id, {
      cve_id: vuln.cve_id,
      cvss: cvss,
      cost: cost,
      deltaEal: deltaEalMap[vuln.cve_id] || deltaEal,
      pluginName: vuln.plugin_name || 'Nessus Vulnerability Plugin',
      host: vuln.host || '192.168.1.10',
      port: vuln.port || 80,
    });
  });

  const patchItems = Array.from(cveMap.values());

  // Sort by selected status then Delta EAL descending
  patchItems.sort((a, b) => {
    const aSelected = selectedCvesSet.has(a.cve_id) ? 1 : 0;
    const bSelected = selectedCvesSet.has(b.cve_id) ? 1 : 0;
    if (aSelected !== bSelected) return bSelected - aSelected;
    return b.deltaEal - a.deltaEal;
  });

  const totalSelectedCost = patchItems
    .filter((item) => selectedCvesSet.has(item.cve_id))
    .reduce((sum, item) => sum + item.cost, 0);

  const budget = optimizationResults?.budget || 0;

  return (
    <div className="view-card patch-action-card font-sans">
      <div className="card-header">
        <div>
          <h3 className="card-title font-mono">
            <span className="title-icon">🛡️</span> PuLP 0/1 Knapsack Patch Optimization Action List
          </h3>
          <p className="card-subtitle">
            Remediations prioritized strictly to maximize total Expected Annual Loss reduction (ΔEAL) under target budget constraint
          </p>
        </div>
        <div className="investment-summary-pill font-mono">
          <span className="summary-label">ALLOCATED INVESTMENT</span>
          <div className="summary-values">
            <span className="val-used text-emerald">{formatCurrency(totalSelectedCost)}</span>
            <span className="val-divider">/</span>
            <span className="val-cap text-cyan">{formatCurrency(budget)}</span>
          </div>
        </div>
      </div>

      <div className="table-responsive">
        <table className="styled-patch-table">
          <thead>
            <tr className="font-mono">
              <th>Rank</th>
              <th>CVE Identifier & Plugin Name</th>
              <th>Host : Port</th>
              <th>CVSS & Effort Tier</th>
              <th>Patch Cost</th>
              <th>ΔEAL Risk Reduction</th>
              <th>Efficiency (ROI)</th>
              <th>Optimization Decision</th>
            </tr>
          </thead>
          <tbody>
            {patchItems.map((item, index) => {
              const isSelected = selectedCvesSet.has(item.cve_id);
              const category = getCvssCategory(item.cvss);
              const efficiency = item.cost > 0 ? (item.deltaEal / item.cost).toFixed(1) : 'N/A';

              return (
                <tr key={item.cve_id} className={`patch-row ${isSelected ? 'selected' : 'unselected'}`}>
                  <td className="font-mono text-center">
                    <span className={`rank-badge font-mono ${isSelected ? 'active' : ''}`}>
                      #{index + 1}
                    </span>
                  </td>
                  <td>
                    <div className="cve-info-cell">
                      <span className="cve-tag font-mono">{item.cve_id}</span>
                      <span className="cve-title">{item.pluginName}</span>
                    </div>
                  </td>
                  <td className="font-mono host-cell">
                    {item.host}:{item.port}
                  </td>
                  <td>
                    <span className={`cvss-effort-pill ${category.cls} font-mono`}>
                      <span className="cvss-num">{item.cvss.toFixed(1)}</span>
                      <span className="cvss-sep">—</span>
                      <span className="cvss-tier">{category.label}</span>
                    </span>
                  </td>
                  <td className="font-mono cost-cell">{formatCurrency(item.cost)}</td>
                  <td className="font-mono delta-eal-cell text-emerald">{formatCurrency(item.deltaEal)}</td>
                  <td className="font-mono">
                    <span className="roi-chip font-mono">
                      {efficiency !== 'N/A' ? `${efficiency}x` : 'N/A'}
                    </span>
                  </td>
                  <td>
                    {isSelected ? (
                      <span className="decision-badge selected font-mono">
                        <span className="icon">✓</span> Selected (Remediated)
                      </span>
                    ) : (
                      <span className="decision-badge unselected font-mono">
                        <span className="icon">✕</span> Unselected (Budget Cap)
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
