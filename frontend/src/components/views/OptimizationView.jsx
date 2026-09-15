import React from 'react';
import BudgetControl from '../BudgetControl';
import PatchList from '../PatchList';
import { formatCurrency, formatCurrencyShort } from '../../utils/lecTransformation';

export default function OptimizationView({ data, budget, onBudgetChange, isOptimizing }) {
  const baselineEal = data?.simulation_results?.eal || 0;
  const postOptEal = data?.optimization_results?.post_opt_eal ?? baselineEal;
  const totalCost = data?.optimization_results?.total_cost || 0;
  const remainingBudget = Math.max(0, budget - totalCost);
  const deltaEal = Math.max(0, baselineEal - postOptEal);
  const selectedCves = data?.optimization_results?.selected_cves || [];
  const roiMultiplier = totalCost > 0 ? (deltaEal / totalCost).toFixed(1) : 'N/A';

  return (
    <div className="optimization-view animate-fadeIn">
      {/* Top Optimization Summary Cards */}
      <div className="opt-summary-grid">
        <div className="opt-card border-left-cyan">
          <span className="opt-label font-mono">TARGET BUDGET LIMIT</span>
          <span className="opt-val font-mono text-cyan">{formatCurrency(budget)}</span>
          <span className="opt-sub font-mono">User Investment Cap</span>
        </div>

        <div className="opt-card border-left-purple">
          <span className="opt-label font-mono">SELECTED REMEDIATION COST</span>
          <span className="opt-val font-mono text-purple">{formatCurrency(totalCost)}</span>
          <span className="opt-sub font-mono">{selectedCves.length} Patches Selected</span>
        </div>

        <div className="opt-card border-left-emerald">
          <span className="opt-label font-mono">REMAINING UNALLOCATED BUDGET</span>
          <span className="opt-val font-mono text-emerald">{formatCurrency(remainingBudget)}</span>
          <span className="opt-sub font-mono">Available Surplus</span>
        </div>

        <div className="opt-card border-left-amber">
          <span className="opt-label font-mono">EXPECTED RISK REDUCTION (ΔEAL)</span>
          <span className="opt-val font-mono text-amber">{formatCurrencyShort(deltaEal)}</span>
          <span className="opt-sub font-mono">{roiMultiplier !== 'N/A' ? `${roiMultiplier}x ROI Multiplier` : 'N/A'}</span>
        </div>
      </div>

      {postOptEal === 0 && (
        <div className="zero-risk-notice-banner font-mono" style={{ marginBottom: '1.5rem' }}>
          <span className="notice-icon">🛡️</span>
          <span><strong>Scope Notice:</strong> ₹0 modeled residual exposure across ingested findings — this does not represent zero organizational cyber risk.</span>
        </div>
      )}

      {/* Interactive Budget Control Controls */}
      <BudgetControl
        budget={budget}
        onBudgetChange={onBudgetChange}
        isOptimizing={isOptimizing}
        totalCost={totalCost}
        selectedCount={selectedCves.length}
      />

      {/* Actionable Remediation Priority List Table */}
      <PatchList
        vulnerabilities={data?.vulnerabilities || []}
        optimizationResults={data?.optimization_results}
        perCveRisk={data?.simulation_results?.per_cve_risk || []}
      />
    </div>
  );
}
