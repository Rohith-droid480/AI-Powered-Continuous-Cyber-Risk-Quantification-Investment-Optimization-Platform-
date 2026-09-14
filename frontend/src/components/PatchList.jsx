import React from 'react';
import { formatCurrency, formatCurrencyShort } from '../utils/lecTransformation';

function getCvssCategory(score) {
  if (score >= 9.0) return { label: 'Critical (40h)', cls: 'badge-critical' };
  if (score >= 7.0) return { label: 'High (16h)', cls: 'badge-high' };
  if (score >= 4.0) return { label: 'Medium (8h)', cls: 'badge-medium' };
  return { label: 'Low (4h)', cls: 'badge-low' };
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

  // Populate from per_cve_risk summaries
  perCveSummaries.forEach((item) => {
    cveMap.set(item.cve_id, {
      cve_id: item.cve_id,
      cvss: 7.5,
      deltaEal: item.baseline_eal,
      cost: 32000,
    });
  });

  // Populate/enrich from vulnerabilities array
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
      pluginName: vuln.plugin_name || 'Nessus Plugin',
      host: vuln.host || 'Asset',
    });
  });

  const patchItems = Array.from(cveMap.values());

  // Sort by Delta EAL descending (or selected status then Delta EAL)
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
    <div className="table-card">
      <div className="table-header">
        <div>
          <h3>PuLP 0/1 Knapsack Patch Optimization List</h3>
          <p className="table-subtitle">
            Remediations selected strictly to maximize total ΔEAL (LEF × Expected Loss) under budget constraint
          </p>
        </div>
        <div className="budget-summary-badge font-mono">
          <span>Cost: <strong>{formatCurrency(totalSelectedCost)}</strong></span>
          <span>/</span>
          <span>Budget: <strong>{formatCurrency(budget)}</strong></span>
        </div>
      </div>

      <div className="table-container">
        <table className="patch-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>CVE ID & Description</th>
              <th>CVSS & Tier</th>
              <th>Patch Cost (₹)</th>
              <th>ΔEAL Risk Reduction (₹)</th>
              <th>Efficiency (ΔEAL/Cost)</th>
              <th>Optimization Status</th>
            </tr>
          </thead>
          <tbody>
            {patchItems.map((item, index) => {
              const isSelected = selectedCvesSet.has(item.cve_id);
              const category = getCvssCategory(item.cvss);
              const efficiency = item.cost > 0 ? (item.deltaEal / item.cost).toFixed(1) : 'N/A';

              return (
                <tr key={item.cve_id} className={isSelected ? 'row-selected' : 'row-unselected'}>
                  <td className="font-mono text-center">#{index + 1}</td>
                  <td>
                    <div className="cve-cell">
                      <span className="cve-id font-mono">{item.cve_id}</span>
                      <span className="cve-subtext">{item.pluginName} ({item.host})</span>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${category.cls}`}>{item.cvss.toFixed(1)} — {category.label}</span>
                  </td>
                  <td className="font-mono text-right">{formatCurrency(item.cost)}</td>
                  <td className="font-mono text-right text-emerald font-semibold">
                    {formatCurrency(item.deltaEal)}
                  </td>
                  <td className="font-mono text-right text-cyan">
                    {efficiency !== 'N/A' ? `${efficiency}x` : 'N/A'}
                  </td>
                  <td>
                    {isSelected ? (
                      <span className="status-badge badge-selected font-mono">✓ SELECTED FOR PATCH</span>
                    ) : (
                      <span className="status-badge badge-unselected font-mono">UNSELECTED (BUDGET EXCEEDED)</span>
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
