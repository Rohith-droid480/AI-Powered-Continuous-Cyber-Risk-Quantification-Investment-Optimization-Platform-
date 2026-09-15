import React from 'react';
import KPICards from '../KPICards';
import { formatCurrency, formatCurrencyShort } from '../../utils/lecTransformation';

export default function OverviewView({ data, budget, onNavigate }) {
  const baselineEal = data?.simulation_results?.eal || 0;
  const postOptEal = data?.optimization_results?.post_opt_eal ?? baselineEal;
  const totalCost = data?.optimization_results?.total_cost || 0;
  const deltaEal = Math.max(0, baselineEal - postOptEal);
  const reductionPct = baselineEal > 0 ? ((deltaEal / baselineEal) * 100).toFixed(1) : '0.0';
  const roiMultiplier = totalCost > 0 ? (deltaEal / totalCost).toFixed(1) : 'N/A';
  const selectedCves = data?.optimization_results?.selected_cves || [];

  // Top Risk Drivers sorted by EAL contribution
  const riskDrivers = [...(data?.simulation_results?.per_cve_risk || [])].sort(
    (a, b) => (b.baseline_eal || 0) - (a.baseline_eal || 0)
  );

  return (
    <div className="overview-view animate-fadeIn">
      {/* Executive Headline ROI Summary Bar */}
      <div className="executive-insight-bar">
        <div className="insight-metric border-left-amber">
          <span className="insight-label font-mono">TOTAL INHERENT EXPOSURE</span>
          <span className="insight-value font-mono text-amber">{formatCurrencyShort(baselineEal)}</span>
          <span className="insight-sub font-mono">Simulated Baseline EAL</span>
        </div>

        <div className="insight-metric border-left-emerald">
          <span className="insight-label font-mono">NET RISK REDUCED</span>
          <span className="insight-value font-mono text-emerald">
            {formatCurrencyShort(deltaEal)} <span className="reduction-badge font-mono">-{reductionPct}%</span>
          </span>
          <span className="insight-sub font-mono">Modeled EAL Savings</span>
        </div>

        <div className="insight-metric border-left-cyan">
          <span className="insight-label font-mono">SELECTED INVESTMENT</span>
          <span className="insight-value font-mono text-cyan">{formatCurrency(totalCost)}</span>
          <span className="insight-sub font-mono">{selectedCves.length} Patches Selected</span>
        </div>

        <div className="insight-metric border-left-purple">
          <span className="insight-label font-mono">PORTFOLIO ROI MULTIPLIER</span>
          <span className="insight-value font-mono text-purple">{roiMultiplier !== 'N/A' ? `${roiMultiplier}x` : 'N/A'}</span>
          <span className="insight-sub font-mono">ΔEAL / Investment Cost</span>
        </div>
      </div>

      {/* Hero KPI Risk Summary Cards */}
      <KPICards data={data} budget={budget} />

      {postOptEal === 0 && (
        <div className="zero-risk-notice-banner font-mono">
          <span className="notice-icon">🛡️</span>
          <span><strong>Scope Notice:</strong> ₹0 modeled residual exposure across ingested findings — this does not represent zero organizational cyber risk.</span>
        </div>
      )}

      {/* Grid: Top Risk Drivers + Loss Distribution Summary */}
      <div className="overview-grid">
        {/* Top Risk Drivers */}
        <div className="view-card overview-drivers-card">
          <div className="card-header">
            <div>
              <h3 className="card-title font-mono">
                <span className="title-icon">🔥</span> Top Financial Risk Drivers
              </h3>
              <p className="card-subtitle">Vulnerabilities contributing highest modeled monetary loss</p>
            </div>
            <button
              onClick={() => onNavigate('findings')}
              className="btn-text-link font-mono"
            >
              View All Findings ➔
            </button>
          </div>

          <div className="table-responsive">
            <table className="overview-table">
              <thead>
                <tr className="font-mono">
                  <th>Rank</th>
                  <th>CVE ID</th>
                  <th>EPSS</th>
                  <th>KEV</th>
                  <th>EAL Contribution</th>
                  <th>Remediation Status</th>
                </tr>
              </thead>
              <tbody>
                {riskDrivers.slice(0, 5).map((driver, index) => {
                  const isSelected = selectedCves.includes(driver.cve_id);
                  const vulnMeta = (data?.vulnerabilities || []).find((v) => v.cve_id === driver.cve_id);
                  return (
                    <tr key={driver.cve_id}>
                      <td className="font-mono text-center">
                        <span className="rank-pill font-mono">#{index + 1}</span>
                      </td>
                      <td className="font-mono font-bold text-white">{driver.cve_id}</td>
                      <td className="font-mono">
                        <span className={`epss-tag ${vulnMeta?.epss_score > 0.8 ? 'high' : 'medium'}`}>
                          {((vulnMeta?.epss_score || 0.5) * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td>
                        {vulnMeta?.is_kev ? (
                          <span className="status-badge kev font-mono">CISA KEV</span>
                        ) : (
                          <span className="status-badge normal font-mono">Standard</span>
                        )}
                      </td>
                      <td className="font-mono text-amber font-bold">
                        {formatCurrency(driver.baseline_eal)}
                      </td>
                      <td>
                        {isSelected ? (
                          <span className="status-badge selected font-mono">Selected (Remediated)</span>
                        ) : (
                          <span className="status-badge unselected font-mono">Unselected</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Distribution Summary Card */}
        <div className="view-card overview-distribution-card">
          <div className="card-header">
            <div>
              <h3 className="card-title font-mono">
                <span className="title-icon">📊</span> Loss Percentile Distribution
              </h3>
              <p className="card-subtitle">Simulation trial percentile thresholds</p>
            </div>
            <button
              onClick={() => onNavigate('risk')}
              className="btn-text-link font-mono"
            >
              Full Monte Carlo ➔
            </button>
          </div>

          <div className="percentile-summary-list">
            <div className="percentile-row">
              <span className="percentile-label font-mono">P10 (10th Percentile)</span>
              <span className="percentile-val font-mono">{formatCurrency(data?.simulation_results?.p10)}</span>
            </div>
            <div className="percentile-row">
              <span className="percentile-label font-mono">P50 (Median Annual Loss)</span>
              <span className="percentile-val font-mono">{formatCurrency(data?.simulation_results?.p50)}</span>
            </div>
            <div className="percentile-row text-amber">
              <span className="percentile-label font-mono">P90 (90th Percentile)</span>
              <span className="percentile-val font-mono">{formatCurrency(data?.simulation_results?.p90)}</span>
            </div>
            <div className="percentile-row text-rose">
              <span className="percentile-label font-mono">P95 (VaR95 Tail Threshold)</span>
              <span className="percentile-val font-mono">{formatCurrency(data?.simulation_results?.var_95)}</span>
            </div>
            <div className="percentile-row text-rose font-bold">
              <span className="percentile-label font-mono">P99 (Extreme Loss Event)</span>
              <span className="percentile-val font-mono">{formatCurrency(data?.simulation_results?.p99)}</span>
            </div>
          </div>

          <div className="distribution-explainer font-mono">
            <span className="info-icon">ℹ️</span>
            <span>100,000 Monte Carlo trials executed per FAIR-aligned Poisson-Lognormal model.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
