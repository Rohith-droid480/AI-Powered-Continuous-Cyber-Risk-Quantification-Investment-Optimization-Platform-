import React from 'react';
import LossExceedanceCurve from '../LossExceedanceCurve';
import { formatCurrency, formatCurrencyShort } from '../../utils/lecTransformation';

export default function QuantitativeRiskView({ data }) {
  const baseline = data?.simulation_results || {};
  const postOpt = data?.post_opt_simulation_results || {};

  return (
    <div className="quantitative-risk-view animate-fadeIn">
      {/* Top Quantitative KPI Grid */}
      <div className="quant-kpi-grid">
        <div className="quant-kpi-card border-left-amber">
          <span className="quant-kpi-label font-mono">BASELINE EXPECTED ANNUAL LOSS</span>
          <span className="quant-kpi-val font-mono text-amber">{formatCurrency(baseline.eal)}</span>
          <span className="quant-kpi-sub font-mono">Distribution Mean (100,000 trials)</span>
        </div>

        <div className="quant-kpi-card border-left-rose">
          <span className="quant-kpi-label font-mono">VALUE AT RISK (VaR95)</span>
          <span className="quant-kpi-val font-mono text-rose">{formatCurrency(baseline.var_95)}</span>
          <span className="quant-kpi-sub font-mono">95% Exceedance Threshold</span>
        </div>

        <div className="quant-kpi-card border-left-rose">
          <span className="quant-kpi-label font-mono">CONDITIONAL VaR (CVaR95)</span>
          <span className="quant-kpi-val font-mono text-rose">{formatCurrency(baseline.cvar_95)}</span>
          <span className="quant-kpi-sub font-mono">Worst 5% Expected Loss</span>
        </div>

        <div className="quant-kpi-card border-left-emerald">
          <span className="quant-kpi-label font-mono">POST-OPT RESIDUAL EAL</span>
          <span className="quant-kpi-val font-mono text-emerald">{formatCurrency(data?.optimization_results?.post_opt_eal)}</span>
          <span className="quant-kpi-sub font-mono">After Selected Remediations</span>
        </div>
      </div>

      {/* Centerpiece Loss Exceedance Curve */}
      <LossExceedanceCurve
        baselineLec={data?.baseline_lec}
        postOptLec={data?.post_opt_lec}
        var95Baseline={baseline.var_95}
      />

      {/* Educational Quantitative Explanation Panel */}
      <div className="view-card quant-explanation-card font-mono">
        <h4 className="explanation-title font-mono">
          <span className="info-icon">📖</span> Understanding the Loss Exceedance Curve (CCDF)
        </h4>
        <div className="explanation-grid">
          <div className="exp-item">
            <span className="exp-heading text-amber">Baseline Distribution (Amber)</span>
            <p className="exp-text">
              Represents the empirical Complementary Cumulative Distribution Function (CCDF) of 100,000 Monte Carlo simulated loss trials prior to remediation.
            </p>
          </div>
          <div className="exp-item">
            <span className="exp-heading text-emerald">Post-Optimization Residual Distribution (Emerald)</span>
            <p className="exp-text">
              Represents the residual annual loss distribution after applying the PuLP-selected remediation package within your target budget constraint.
            </p>
          </div>
          <div className="exp-item">
            <span className="exp-heading text-rose">Value at Risk (VaR95 Threshold)</span>
            <p className="exp-text">
              The monetary loss threshold that is exceeded in only 5% of simulated annual outcomes ($P_{95}$).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
