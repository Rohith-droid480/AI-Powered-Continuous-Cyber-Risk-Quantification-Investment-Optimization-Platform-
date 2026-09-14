import React, { useState } from 'react';
import { formatCurrency } from '../utils/lecTransformation';

export default function BudgetControl({ currentBudget, onBudgetChange, isOptimizing }) {
  const [inputValue, setInputValue] = useState(currentBudget || 150000);

  const presets = [
    { label: 'Low Budget (₹50k)', value: 50000 },
    { label: 'Medium Demo (₹150k)', value: 150000 },
    { label: 'Full Scope (₹300k)', value: 300000 },
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
    <div className="budget-card">
      <div className="budget-header">
        <div>
          <h3>Remediation Budget Constraint</h3>
          <p className="budget-subtitle">
            Adjust budget limit to trigger real-time 0/1 Knapsack optimization and Monte Carlo re-simulation
          </p>
        </div>
        <div className="budget-current-value font-mono">
          {formatCurrency(currentBudget)}
        </div>
      </div>

      <div className="budget-presets">
        {presets.map((p) => (
          <button
            key={p.value}
            type="button"
            className={`preset-btn ${currentBudget === p.value ? 'active' : ''}`}
            onClick={() => handlePresetClick(p.value)}
            disabled={isOptimizing}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="slider-container">
        <input
          type="range"
          min="10000"
          max="400000"
          step="10000"
          value={inputValue}
          onChange={handleSliderChange}
          disabled={isOptimizing}
          className="budget-slider"
        />
        <div className="slider-labels font-mono">
          <span>Min: ₹10k</span>
          <span>Target: {formatCurrency(inputValue)}</span>
          <span>Max: ₹400k</span>
        </div>
      </div>

      {isOptimizing && (
        <div className="optimizing-indicator font-mono text-cyan">
          <span className="spinner"></span> Re-running PuLP 0/1 Knapsack Optimization & Monte Carlo Re-simulation...
        </div>
      )}
    </div>
  );
}
