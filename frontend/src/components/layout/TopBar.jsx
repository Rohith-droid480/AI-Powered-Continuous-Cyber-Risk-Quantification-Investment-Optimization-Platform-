import React from 'react';

const TAB_TITLES = {
  overview: { title: 'Executive Risk Overview', desc: 'Financial Exposure & Remediation Strategy' },
  scan: { title: 'Scan & Ingestion Pipeline', desc: 'Layer 1 Nessus XML Parser & Execution Pipeline' },
  risk: { title: 'Quantitative Risk Analysis', desc: 'Layer 4 Vectorized Monte Carlo Distribution' },
  optimization: { title: 'Investment Optimization', desc: 'Layer 5 PuLP 0/1 Knapsack Remediation Solver' },
  findings: { title: 'Vulnerability Findings & Threat Intel', desc: 'Layer 1+2 Discovered CVEs, EPSS & KEV Flags' },
  methodology: { title: 'Model Architecture & Methodology', desc: 'Layers 1–6 Integration, FAIR Model & Disclosures' },
};

export default function TopBar({ activeTab, setActiveTab, apiConnected, budget, data }) {
  const currentInfo = TAB_TITLES[activeTab] || TAB_TITLES.overview;
  const cveCount = data?.vulnerabilities?.length || 5;

  return (
    <header className="app-topbar">
      <div className="topbar-title-box">
        <h1 className="topbar-page-title">{currentInfo.title}</h1>
        <p className="topbar-page-desc font-mono">{currentInfo.desc}</p>
      </div>

      <div className="topbar-actions">
        {/* Dataset Meta Pill */}
        <div className="topbar-meta-pill font-mono">
          <span className="pill-dot"></span>
          <span>{cveCount} CVEs Analyzed</span>
        </div>

        {/* Quick Action Buttons */}
        <button
          onClick={() => setActiveTab('scan')}
          className="topbar-btn secondary font-mono"
        >
          <span>📡</span> Upload Scan
        </button>

        <button
          onClick={() => setActiveTab('optimization')}
          className="topbar-btn primary font-mono"
        >
          <span>⚡</span> Budget: ₹{(budget / 1000).toFixed(0)}k
        </button>
      </div>
    </header>
  );
}
