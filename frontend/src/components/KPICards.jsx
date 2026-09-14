import React from 'react';
import { formatCurrency, formatCurrencyShort } from '../utils/lecTransformation';

export default function KPICards({ simulationResults, optimizationResults, postOptSimulation }) {
  if (!simulationResults) return null;

  const baselineEal = simulationResults.eal || 0;
  const var95 = simulationResults.var_95 || 0;
  const cvar95 = simulationResults.cvar_95 || 0;

  const p10 = simulationResults.p10 ?? 0;
  const p50 = simulationResults.p50 ?? 0;
  const p90 = simulationResults.p90 ?? (var95 * 0.6);
  const p99 = simulationResults.p99 ?? (var95 * 2.3);

  const postOptEal = optimizationResults?.post_opt_eal ?? baselineEal;
  const totalCost = optimizationResults?.total_cost || 0;
  const deltaEal = Math.max(0, baselineEal - postOptEal);
  const reductionPct = baselineEal > 0 ? ((deltaEal / baselineEal) * 100).toFixed(1) : '0.0';
  const roiMultiplier = totalCost > 0 ? (deltaEal / totalCost).toFixed(2) : 'N/A';

  return (
    <div className="kpi-section-wrapper">
      <div className="kpi-grid">
        {/* 1. Baseline EAL */}
        <div className="kpi-card baseline">
          <div className="kpi-header">
            <span className="kpi-title">Baseline Expected Annual Loss (EAL)</span>
            <span className="kpi-badge font-mono">Pre-Remediation Mean</span>
          </div>
          <div className="kpi-value text-amber">{formatCurrency(baselineEal)}</div>
          <div className="kpi-subtitle font-mono">
            Dist Range (P10–P90): {formatCurrencyShort(p10)} — {formatCurrencyShort(p90)}
          </div>
          <div className="kpi-context text-muted">
            Annualized expected breach loss (FAIR calibrated mean)
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
          <div className="kpi-subtitle font-mono">
            Residual Expected Loss (Post-Opt P10–P90: ₹0.00 — {formatCurrencyShort(postOptSimulation?.p90 || (optimizationResults?.post_opt_var_95 * 0.6) || 0)})
          </div>
          <div className="kpi-context text-muted">
            Residual risk after {optimizationResults?.selected_cves?.length || 0} selected CVE patches
          </div>
        </div>

        {/* 3. Value at Risk (VaR 95%) */}
        <div className="kpi-card var">
          <div className="kpi-header">
            <span className="kpi-title">Value at Risk 95% (VaR95)</span>
            <span className="kpi-badge font-mono">95th Percentile</span>
          </div>
          <div className="kpi-value text-cyan">{formatCurrency(var95)}</div>
          <div className="kpi-subtitle font-mono">
            Dist Context: P90 {formatCurrencyShort(p90)} / P99 {formatCurrencyShort(p99)}
          </div>
          <div className="kpi-context text-muted">
            Loss threshold exceeded in only 5% of simulation trial years
          </div>
        </div>

        {/* 4. Conditional VaR (CVaR 95%) */}
        <div className="kpi-card cvar">
          <div className="kpi-header">
            <span className="kpi-title">Conditional VaR 95% (CVaR95)</span>
            <span className="kpi-badge font-mono">Tail Risk</span>
          </div>
          <div className="kpi-value text-purple">{formatCurrency(cvar95)}</div>
          <div className="kpi-subtitle font-mono">
            Tail Mean: Loss magnitude in worst 5% of trial years
          </div>
          <div className="kpi-context text-muted">
            Expected magnitude when 95th percentile threshold is exceeded
          </div>
        </div>

        {/* 5. Remediation Patch Cost */}
        <div className="kpi-card cost">
          <div className="kpi-header">
            <span className="kpi-title">Selected Remediation Cost</span>
            <span className="kpi-badge font-mono">PuLP 0/1 Knapsack</span>
          </div>
          <div className="kpi-value text-blue">{formatCurrency(totalCost)}</div>
          <div className="kpi-subtitle font-mono">
            Budget Cap: {formatCurrency(optimizationResults?.budget || 0)}
          </div>
          <div className="kpi-context text-muted">
            Labor effort cost for selected remediations
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
          <div className="kpi-subtitle font-mono">
            Total ΔEAL: {formatCurrencyShort(deltaEal)}
          </div>
          <div className="kpi-context text-muted">
            Annualized loss reduction per rupee spent
          </div>
        </div>
      </div>

      <div className="kpi-statistical-disclaimer font-mono">
        <span>* Note: P10/P50/P90/P99 represent percentiles of the simulated annual loss distribution, NOT confidence intervals for the expected value (EAL).</span>
      </div>
    </div>
  );
}
