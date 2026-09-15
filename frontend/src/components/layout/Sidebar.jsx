import React from 'react';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: '📊', description: 'Executive Risk Overview' },
  { id: 'scan', label: 'Scan & Ingestion', icon: '📡', description: 'Layer 1 Ingestion Pipeline' },
  { id: 'risk', label: 'Quantitative Risk', icon: '📈', description: 'Layer 4 Monte Carlo Analysis' },
  { id: 'optimization', label: 'Investment Optimization', icon: '⚡', description: 'Layer 5 PuLP Solver' },
  { id: 'findings', label: 'Findings', icon: '🔍', description: 'Layer 1+2 Vulnerability List' },
  { id: 'methodology', label: 'Model & Methodology', icon: '📘', description: 'Layers 1–6 Architecture' },
];

export default function Sidebar({ activeTab, setActiveTab, apiConnected, activeScanName = 'enterprise_perimeter_scan.nessus' }) {
  return (
    <aside className="app-sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand font-mono">
        <div className="brand-icon-box">
          <span className="brand-logo">🛡️</span>
        </div>
        <div className="brand-text">
          <h2 className="brand-title">CYBER RISK</h2>
          <span className="brand-subtitle">Quantification Engine</span>
        </div>
      </div>

      {/* Scope Identifier */}
      <div className="sidebar-scope-box font-mono">
        <div className="scope-label">ACTIVE SCAN SCOPE</div>
        <div className="scope-value" title={activeScanName}>
          <span className="scope-dot"></span>
          {activeScanName}
        </div>
      </div>

      {/* Main Navigation Menu */}
      <nav className="sidebar-nav">
        <div className="nav-section-title font-mono">CORE PLATFORM</div>
        {NAV_ITEMS.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <div className="nav-label-box">
                <span className="nav-label">{item.label}</span>
                <span className="nav-desc">{item.description}</span>
              </div>
              {isActive && <div className="nav-indicator"></div>}
            </button>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div className="sidebar-footer font-mono">
        <div className="system-status-badge">
          <span className={`status-dot ${apiConnected ? 'connected' : 'demo'}`}></span>
          <span className="status-text">
            {apiConnected ? 'API Connected (8000)' : 'Demo Mode Active'}
          </span>
        </div>
        <div className="architecture-version">
          <span>Architecture: 6-Layer Integrated</span>
        </div>
      </div>
    </aside>
  );
}
