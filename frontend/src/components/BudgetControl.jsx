import React, { useState, useEffect } from 'react';
import { formatCurrency } from '../utils/lecTransformation';

export default function BudgetControl({ budget, currentBudget: altBudget, onBudgetChange, isOptimizing, totalCost, selectedCount }) {
  const activeBudget = budget ?? altBudget ?? 150000;
  const [inputValue, setInputValue] = useState(activeBudget);

  useEffect(() => {
    setInputValue(activeBudget);
  }, [activeBudget]);

  const presets = [
    { label: 'Low Budget (₹50k)', value: 50000, desc: 'Targeted Remediation' },
    { label: 'Medium Demo (₹150k)', value: 150000, desc: 'High ROI Balance' },
    { label: 'Full Scope (₹300k)', value: 300000, desc: '100% Remediated' },
  ];

  const handleSliderChange = (e) => {
    const val = Number(e.target.value);
    setInputValue(val);
    onBudgetChange(val);
  };

  const handlePresetClick = (val) => {
    setInputValue(val);
    onBudgetChange(val);
  };

  return (
    <div className="view-card budget-card font-sans">
      <div className="card-header">
        <div>
          <h3 className="card-title font-mono">
            <span className="title-icon">⚡</span> Remediation Budget Constraint
          </h3>
          <p className="card-subtitle">
            Adjust investment limit to trigger real-time PuLP 0/1 Knapsack optimization and Monte Carlo re-simulation
          </p>
        </div>
        <div className="budget-value-badge font-mono">
          <span className="badge-label">TARGET BUDGET</span>
          <span className="badge-val text-cyan">{formatCurrency(activeBudget)}</span>
        </div>
      </div>

      {/* Preset Chips Row */}
      <div className="budget-presets-container">
        <div className="presets-label font-mono">BUDGET PRESETS:</div>
        <div className="presets-grid">
          {presets.map((p) => {
            const isActive = activeBudget === p.value;
            return (
              <button
                key={p.value}
                type="button"
                className={`budget-preset-chip font-mono ${isActive ? 'active' : ''}`}
                onClick={() => handlePresetClick(p.value)}
                disabled={isOptimizing}
              >
                <div className="chip-content">
                  <span className="chip-label">{p.label}</span>
                  <span className="chip-desc">{p.desc}</span>
                </div>
                {isActive && <span className="chip-indicator">✓ Active</span>}
              </button>
            );
          })}
        </div>
      </div>

      {/* Slider Control */}
      <div className="budget-slider-box">
        <div className="slider-header font-mono">
          <span className="slider-title">RANGE CONTROLLER</span>
          <span className="slider-current text-cyan">{formatCurrency(inputValue)}</span>
        </div>

        <input
          type="range"
          min="10000"
          max="400000"
          step="10000"
          value={inputValue}
          onChange={handleSliderChange}
          disabled={isOptimizing}
          className="custom-budget-slider"
        />

        <div className="slider-ticks font-mono">
          <span>Min: ₹10k</span>
          <span className="tick-active">Current: {formatCurrency(inputValue)}</span>
          <span>Max: ₹400k</span>
        </div>
      </div>

      {isOptimizing && (
        <div className="optimizing-status-box font-mono animate-fadeIn">
          <span className="spinner"></span>
          <span>Solving PuLP Integer Program & Resimulating 100,000 Monte Carlo Trials...</span>
        </div>
      )}
    </div>
  );
}
