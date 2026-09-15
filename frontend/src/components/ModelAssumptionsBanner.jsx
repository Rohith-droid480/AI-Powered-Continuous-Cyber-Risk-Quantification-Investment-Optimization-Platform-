import React from 'react';

export default function ModelAssumptionsBanner() {
  return (
    <div className="assumptions-card font-mono">
      <div className="assumptions-header">
        <span className="info-icon">ℹ️</span>
        <span className="assumptions-title">Model Calibration & Architecture Transparency</span>
      </div>

      <div className="assumptions-grid">
        <div className="assumption-item">
          <strong>FAIR Structural Contract:</strong> LEF = TEF × Vuln (Loss Event Frequency relationship).
        </div>
        <div className="assumption-item">
          <strong>Primary Loss Anchor:</strong> Anchored to IBM 2026 India breach mean (₹255M). LogNormal CV=2.0 (μ ≈ 18.55, σ ≈ 1.27) is a mathematical modeling assumption.
        </div>
        <div className="assumption-item">
          <strong>Secondary Loss Margin:</strong> 0.4 × Primary Loss (illustrative conservative margin covering DPDPA/regulatory exposure).
        </div>
        <div className="assumption-item">
          <strong>Patch Cost Tiers:</strong> CVSS effort hours (Critical 40h, High 16h, Medium 8h, Low 4h @ ₹2,000/hr labor rate) — our own estimated assumption.
        </div>
        <div className="assumption-item">
          <strong>Threat Intelligence Database:</strong> Local SQLite database (`app/data/threat_intel.db`) lookup for EPSS probability & CISA KEV flags — no external network dependency.
        </div>
      </div>
    </div>
  );
}
