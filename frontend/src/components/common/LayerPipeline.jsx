import React, { useState } from 'react';

const PIPELINE_LAYERS = [
  {
    id: 1,
    name: 'Layer 1: Ingestion',
    shortName: 'L1 Ingest',
    file: 'app/ingestion/parser.py',
    purpose: 'Parses raw Nessus XML scan files and extracts structured vulnerability findings.',
    input: 'Raw .nessus XML file payload',
    output: 'Structured list of vulnerability records (CVE, Host, Port, Severity)',
    math: 'XML DOM parsing, CVE extraction & severity normalization',
    uiComponent: 'ScanIngestionView / UploadFlow',
    badge: 'Ingestion',
    color: 'border-blue-500/30 text-blue-400'
  },
  {
    id: 2,
    name: 'Layer 2: Threat Enrichment',
    shortName: 'L2 Enrich',
    file: 'app/enrichment/epss_lookup.py',
    purpose: 'Enriches vulnerabilities with threat intelligence (EPSS probability & CISA KEV status).',
    input: 'CVE IDs from Layer 1',
    output: 'Enriched vulnerability records with EPSS scores (0.0 - 1.0) & KEV flags',
    math: 'SQLite lookups & EPSS probability mapping',
    uiComponent: 'FindingsView / RiskDrivers',
    badge: 'Threat Intel',
    color: 'border-purple-500/30 text-purple-400'
  },
  {
    id: 3,
    name: 'Layer 3: FAIR Calibration',
    shortName: 'L3 Calibrate',
    file: 'app/risk/fair_calibrator.py',
    purpose: 'Calibrates Threat Event Frequency (TEF) and Vulnerability (VLA) into Loss Event Frequency (LEF) and Lognormal loss magnitude parameters.',
    input: 'EPSS, CVSS, asset value & labor cost assumptions',
    output: 'Lognormal loss parameters (μ, σ, min, mode, max) per CVE',
    math: 'FAIR lognormal parameter estimation & PERT-like bounds calibration',
    uiComponent: 'MethodologyView / ModelAssumptions',
    badge: 'FAIR Model',
    color: 'border-amber-500/30 text-amber-400'
  },
  {
    id: 4,
    name: 'Layer 4: Monte Carlo Simulation',
    shortName: 'L4 Simulate',
    file: 'app/simulation/engine.py',
    purpose: 'Executes 100,000 empirical annual-loss trials using vectorized NumPy lognormal sampling.',
    input: 'Layer 3 calibrated lognormal loss parameters (μ, σ, LEF)',
    output: 'Expected Annual Loss (EAL), VaR95, CVaR95, P10-P99 distribution & 100-point LEC',
    math: 'Vectorized NumPy lognormal trials: Loss = Sum(Lognormal(μ, σ)) across Poisson(LEF)',
    uiComponent: 'QuantitativeRiskView / LossExceedanceCurve',
    badge: 'Monte Carlo',
    color: 'border-emerald-500/30 text-emerald-400'
  },
  {
    id: 5,
    name: 'Layer 5: Remediation Optimization',
    shortName: 'L5 Optimize',
    file: 'app/optimization/pulp_optimizer.py',
    purpose: 'Solves a 0/1 Knapsack optimization problem using PuLP to maximize EAL reduction within the user budget.',
    input: 'Per-CVE baseline EAL, remediation labor costs, available budget limit',
    output: 'Optimal subset of patches to apply, total cost, and post-optimization resimulation',
    math: 'PuLP 0/1 Integer Programming: Maximize Sum(ΔEAL_i * x_i) s.t. Sum(Cost_i * x_i) <= Budget',
    uiComponent: 'OptimizationView / BudgetControl / PatchList',
    badge: 'PuLP Solver',
    color: 'border-cyan-500/30 text-cyan-400'
  },
  {
    id: 6,
    name: 'Layer 6: Executive Dashboard',
    shortName: 'L6 Present',
    file: 'frontend/src/App.jsx & components/',
    purpose: 'Presents executive portfolio risk, tail-risk curves, budget controls, and actionable patch priority lists.',
    input: 'Compact API response payload (16.29 KB)',
    output: 'Interactive React application shell & multi-page executive portal',
    math: 'Frontend aggregation, Recharts area curves & UI rendering',
    uiComponent: 'AppShell / View Components',
    badge: 'Executive UX',
    color: 'border-indigo-500/30 text-indigo-400'
  }
];

export default function LayerPipeline({ currentLayer = 6, compact = false }) {
  const [selectedLayer, setSelectedLayer] = useState(PIPELINE_LAYERS[0]);

  return (
    <div className="layer-pipeline-card">
      <div className="pipeline-header">
        <div>
          <h3 className="pipeline-title font-mono">
            <span className="title-icon">⚡</span> 6-Layer Architecture Pipeline Execution
          </h3>
          <p className="pipeline-subtitle">
            Click any layer to inspect file source, inputs, outputs, mathematical operations, and UI mapping.
          </p>
        </div>
        <span className="pipeline-badge font-mono">Integrated Pipeline</span>
      </div>

      {/* Pipeline Steps Bar */}
      <div className="pipeline-steps-grid">
        {PIPELINE_LAYERS.map((layer, index) => {
          const isSelected = selectedLayer.id === layer.id;
          const isActive = layer.id <= currentLayer;
          return (
            <React.Fragment key={layer.id}>
              <div
                onClick={() => setSelectedLayer(layer)}
                className={`pipeline-step-node ${isSelected ? 'selected' : ''} ${isActive ? 'active' : ''}`}
              >
                <div className="step-num font-mono">{layer.id}</div>
                <div className="step-label font-mono">{layer.shortName}</div>
                <div className="step-badge">{layer.badge}</div>
              </div>
              {index < PIPELINE_LAYERS.length - 1 && (
                <div className="pipeline-arrow font-mono">➔</div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Layer Detail Inspector Panel */}
      {selectedLayer && (
        <div className="layer-detail-panel animate-fadeIn">
          <div className="panel-top">
            <div className="panel-title-group">
              <span className="layer-number font-mono">Layer {selectedLayer.id}</span>
              <h4 className="layer-name">{selectedLayer.name}</h4>
            </div>
            <code className="layer-file-path font-mono">{selectedLayer.file}</code>
          </div>

          <p className="layer-description">{selectedLayer.purpose}</p>

          <div className="layer-specs-grid">
            <div className="spec-box">
              <span className="spec-label font-mono">Data Input</span>
              <p className="spec-value">{selectedLayer.input}</p>
            </div>
            <div className="spec-box">
              <span className="spec-label font-mono">Data Output</span>
              <p className="spec-value">{selectedLayer.output}</p>
            </div>
            <div className="spec-box">
              <span className="spec-label font-mono">Mathematical Operation</span>
              <code className="spec-code font-mono">{selectedLayer.math}</code>
            </div>
            <div className="spec-box">
              <span className="spec-label font-mono">UI Component Representation</span>
              <span className="spec-component font-mono">{selectedLayer.uiComponent}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
