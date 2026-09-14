import React from 'react';
import { formatCurrency, formatCurrencyShort } from '../utils/lecTransformation';

export default function KPICards({ simulationResults, optimizationResults, postOptSimulation }) {
  if (!simulationResults) return null;

  const baselineEal = simulationResults.eal || 0;
  const var95 = simulationResults.var_95 || 0;
  const cvar95 = simulationResults.cvar_95 || 0;

  const postOptEal = optimizationResults?.post_opt_eal ?? baselineEal;
  const totalCost = optimizationResults?.total_cost || 0;
  const deltaEal = Math.max(0, baselineEal - postOptEal);
  const reductionPct = baselineEal > 0 ? ((deltaEal / baselineEal) * 100).toFixed(1) : '0.0';
  const roiMultiplier = totalCost > 0 ? (deltaEal / totalCost).toFixed(2) : 'N/A';

  return (
    <div className="kpi-grid">
      {/* 1. Baseline EAL */}
      <div className="kpi-card baseline">
        <div className="kpi-header">
          <span className="kpi-title">Baseline Expected Annual Loss (EAL)</span>
          <span className="kpi-badge font-mono">Pre-Remediation</span>
        </div>
        <div className="kpi-value text-amber">{formatCurrency(baselineEal)}</div>
        <div className="kpi-subtitle">
          Annualized mean financial breach expectation (FAIR calibrated)
        </div>
      </div>

      {/* 2. Optimized EAL */}
      <div className="kpi-card optimized">
        <div className="kpi-header">
          <span className="kpi-title">Post-Optimization EAL</span>
          <span className="kpi-badge badge-green font-mono">
            -{reductionPct}% Risk
          </span>
        </div>
        <div className="kpi-value text-emerald">{formatCurrency(postOptEal)}</div>
        <div className="kpi-subtitle">
          Residual expected annual loss after {optimizationResults?.selected_cves?.length || 0} CVE patches
        </div>
      </div>

      {/* 3. Value at Risk (VaR 95%) */}
      <div className="kpi-card var">
        <div className="kpi-header">
          <span className="kpi-title">Value at Risk 95% (VaR95)</span>
          <span className="kpi-badge font-mono">95th Percentile</span>
        </div>
        <div className="kpi-value text-cyan">{formatCurrency(var95)}</div>
        <div className="kpi-subtitle">
          Annual loss threshold exceeded in only 5% of simulation trial years
        </div>
      </div>

      {/* 4. Conditional VaR (CVaR 95%) */}
      <div className="kpi-card cvar">
        <div className="kpi-header">
          <span className="kpi-title">Conditional VaR 95% (CVaR95)</span>
          <span className="kpi-badge font-mono">Tail Loss</span>
        </div>
        <div className="kpi-value text-purple">{formatCurrency(cvar95)}</div>
        <div className="kpi-subtitle">
          Expected severe loss magnitude when the 95th percentile is exceeded
        </div>
      </div>

      {/* 5. Remediation Patch Cost */}
      <div className="kpi-card cost">
        <div className="kpi-header">
          <span className="kpi-title">Selected Remediation Cost</span>
          <span className="kpi-badge font-mono">PuLP 0/1 Knapsack</span>
        </div>
        <div className="kpi-value text-blue">{formatCurrency(totalCost)}</div>
        <div className="kpi-subtitle">
          Total labor cost constrained under {formatCurrency(optimizationResults?.budget || 0)} budget
        </div>
      </div>

      {/* 6. EAL Reduction Efficiency */}
      <div className="kpi-card roi">
        <div className="kpi-header">
          <span className="kpi-title">Risk Reduction Efficiency</span>
          <span className="kpi-badge font-mono">ΔEAL / Cost</span>
        </div>
        <div className="kpi-value text-cyan">
          {roiMultiplier !== 'N/A' ? `${roiMultiplier}x` : 'N/A'}
        </div>
        <div className="kpi-subtitle">
          {formatCurrencyShort(deltaEal)} loss reduction per rupee spent
        </div>
      </div>
    </div>
  );
}
