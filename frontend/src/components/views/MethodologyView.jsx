import React from 'react';
import LayerPipeline from '../common/LayerPipeline';
import ModelAssumptionsBanner from '../ModelAssumptionsBanner';

export default function MethodologyView() {
  return (
    <div className="methodology-view animate-fadeIn">
      {/* Model Scope & Assumptions Banner */}
      <ModelAssumptionsBanner />

      {/* Complete Interactive 6-Layer Pipeline Inspector */}
      <LayerPipeline currentLayer={6} />

      {/* Technical Methodology Cards */}
      <div className="methodology-cards-grid">
        <div className="view-card methodology-card font-mono">
          <h4 className="methodology-card-title">
            <span className="icon">📐</span> FAIR-Aligned Parameter Calibration
          </h4>
          <p className="methodology-card-desc">
            Vulnerability Threat Event Frequency (TEF) and Vulnerability (VLA) parameters are calibrated from EPSS probability scores and CVSS impact scores. Loss magnitudes are fitted to PERT-like min/mode/max bounds and converted into lognormal distribution parameters (μ, σ).
          </p>
        </div>

        <div className="view-card methodology-card font-mono">
          <h4 className="methodology-card-title">
            <span className="icon">🎲</span> 100,000 Trial Monte Carlo Engine
          </h4>
          <p className="methodology-card-desc">
            Executes 100,000 empirical annual-loss trials using vectorized NumPy sampling. For each trial year, Poisson-distributed loss events sample lognormal loss magnitudes to generate an empirical annual-loss probability distribution.
          </p>
        </div>

        <div className="view-card methodology-card font-mono">
          <h4 className="methodology-card-title">
            <span className="icon">⚡</span> PuLP 0/1 Knapsack Remediation Solver
          </h4>
          <p className="methodology-card-desc">
            Remediation patch selection uses integer linear programming (PuLP solver) to maximize total Expected Annual Loss reduction (Sum of ΔEAL_i × x_i) subject to user-defined budget constraints (Sum of Cost_i × x_i ≤ Budget).
          </p>
        </div>

        <div className="view-card methodology-card font-mono">
          <h4 className="methodology-card-title">
            <span className="icon">💼</span> Remediation Labor Cost Assumptions
          </h4>
          <p className="methodology-card-desc">
            Remediation costs are computed from CVSS severity labor effort tiers (Critical = 40h, High = 16h, Medium = 8h, Low = 4h) evaluated at a baseline labor rate of ₹2,000/hour <span className="assumption-note">(our own estimated assumption)</span>.
          </p>
        </div>
      </div>
    </div>
  );
}
