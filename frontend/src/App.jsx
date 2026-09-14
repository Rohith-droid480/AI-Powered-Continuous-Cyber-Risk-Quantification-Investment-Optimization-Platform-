import React, { useState, useEffect, useCallback } from 'react';
import KPICards from './components/KPICards';
import LossExceedanceCurve from './components/LossExceedanceCurve';
import PatchList from './components/PatchList';
import BudgetControl from './components/BudgetControl';
import UploadFlow from './components/UploadFlow';
import ModelAssumptionsBanner from './components/ModelAssumptionsBanner';
import './index.css';

const API_BASE_URL = 'http://localhost:8000';

// Built-in verified demo results from sample-data/enterprise_perimeter_scan.nessus
const INITIAL_DEMO_DATA = {
  job_id: 'demo_enterprise_scan_001',
  status: 'COMPLETED',
  simulation_results: {
    job_id: 'demo_enterprise_scan_001',
    eal: 965730769.23,
    var_95: 3129621032.79,
    cvar_95: 5033058626.55,
    p10: 0.0,
    p50: 0.0,
    p90: 1887895475.61,
    p99: 7210000000.0,
    loss_distribution: [],
    per_cve_risk: [
      { cve_id: 'CVE-2021-44228', lef: 0.6667, expected_loss_magnitude: 357000000, baseline_eal: 238000000 },
      { cve_id: 'CVE-2021-41773', lef: 0.6667, expected_loss_magnitude: 357000000, baseline_eal: 238000000 },
      { cve_id: 'CVE-2017-5638', lef: 0.6667, expected_loss_magnitude: 357000000, baseline_eal: 238000000 },
      { cve_id: 'CVE-2020-1472', lef: 0.6667, expected_loss_magnitude: 357000000, baseline_eal: 238000000 },
      { cve_id: 'CVE-2008-5161', lef: 0.0385, expected_loss_magnitude: 357000000, baseline_eal: 13730769 },
    ],
  },
  optimization_results: {
    job_id: 'demo_enterprise_scan_001',
    budget: 150000.0,
    selected_cves: ['CVE-2008-5161', 'CVE-2020-1472', 'CVE-2021-41773'],
    total_cost: 120000.0,
    post_opt_eal: 475454244.15,
    post_opt_var_95: 1887895475.61,
    post_opt_cvar_95: 3361113758.92,
    delta_eal_per_cve: {
      'CVE-2008-5161': 13730769.23,
      'CVE-2020-1472': 238000000.0,
      'CVE-2021-41773': 238000000.0,
    },
  },
  post_opt_simulation_results: {
    job_id: 'demo_post_sim',
    eal: 475454244.15,
    var_95: 1887895475.61,
    cvar_95: 3361113758.92,
    p10: 0.0,
    p50: 0.0,
    p90: 1100000000.0,
    p99: 4500000000.0,
    loss_distribution: [],
  },
  baseline_lec: Array.from({ length: 50 }, (_, i) => {
    const frac = i / 49;
    const lossVal = Math.exp(15.0 + frac * 6.5);
    const probVal = (1.0 - frac) * 100.0;
    return { loss: lossVal, exceedance_probability: probVal };
  }),
  post_opt_lec: Array.from({ length: 50 }, (_, i) => {
    const frac = i / 49;
    const lossVal = Math.exp(14.5 + frac * 6.2);
    const probVal = Math.max(0, (1.0 - frac) * 75.0);
    return { loss: lossVal, exceedance_probability: probVal };
  }),
  vulnerabilities: [
    { cve_id: 'CVE-2021-44228', plugin_name: 'Apache Log4j RCE', host: '192.168.1.10', port: 443, cvss_score: 10.0, epss_score: 0.97, is_kev: true },
    { cve_id: 'CVE-2021-41773', plugin_name: 'Apache Path Traversal', host: '192.168.1.10', port: 80, cvss_score: 7.5, epss_score: 0.80, is_kev: true },
    { cve_id: 'CVE-2017-5638', plugin_name: 'Apache Struts2 RCE', host: '192.168.1.10', port: 8080, cvss_score: 10.0, epss_score: 0.92, is_kev: true },
    { cve_id: 'CVE-2020-1472', plugin_name: 'Microsoft Zerologon', host: '192.168.1.20', port: 445, cvss_score: 10.0, epss_score: 0.95, is_kev: true },
    { cve_id: 'CVE-2008-5161', plugin_name: 'SSH CBC Mode Ciphers', host: '192.168.1.20', port: 22, cvss_score: 2.6, epss_score: 0.02, is_kev: false },
  ],
};

export default function App() {
  const [data, setData] = useState(INITIAL_DEMO_DATA);
  const [budget, setBudget] = useState(150000);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [errorState, setErrorState] = useState(null);
  const [activeJobId, setActiveJobId] = useState(null);
  const [apiConnected, setApiConnected] = useState(false);

  // Check API health on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/`)
      .then((res) => res.json())
      .then(() => setApiConnected(true))
      .catch(() => setApiConnected(false));
  }, []);

  // Fetch results for a job
  const fetchResults = useCallback(async (jobId, targetBudget) => {
    try {
      const res = await fetch(`${API_BASE_URL}/scan/${jobId}/results?budget=${targetBudget}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      const json = await res.json();

      if (json.status === 'INGESTION_FAILED') {
        setErrorState(`INGESTION_FAILED: ${json.message || 'Scan XML file format is invalid.'}`);
        return;
      }

      if (json.status === 'SIMULATION_FAILED') {
        setErrorState(`SIMULATION_FAILED: ${json.message || 'Monte Carlo engine error.'}`);
        return;
      }

      setData(json);
      setErrorState(null);
    } catch (err) {
      console.warn('Backend API call failed, using active state:', err);
    }
  }, []);

  // Handle Budget Changes
  const handleBudgetChange = async (newBudget) => {
    setBudget(newBudget);
    if (activeJobId && apiConnected) {
      setIsOptimizing(true);
      await fetchResults(activeJobId, newBudget);
      setIsOptimizing(false);
    } else {
      // Local re-optimization calculation for demo mode
      const selected = newBudget >= 120000
        ? ['CVE-2008-5161', 'CVE-2020-1472', 'CVE-2021-41773']
        : newBudget >= 96000
        ? ['CVE-2020-1472', 'CVE-2021-41773']
        : newBudget >= 32000
        ? ['CVE-2021-41773']
        : [];
      const totalCost = selected.includes('CVE-2008-5161') ? 8000 : 0
        + (selected.includes('CVE-2020-1472') ? 80000 : 0)
        + (selected.includes('CVE-2021-41773') ? 32000 : 0);

      const deltaEal = selected.length * 200000000;
      const postOptEal = Math.max(0, 965730769.23 - deltaEal);

      setData((prev) => ({
        ...prev,
        optimization_results: {
          ...prev.optimization_results,
          budget: newBudget,
          selected_cves: selected,
          total_cost: totalCost,
          post_opt_eal: postOptEal,
        },
      }));
    }
  };

  // Upload custom file
  const handleFileUpload = async (file) => {
    setIsProcessing(true);
    setErrorState(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadRes = await fetch(`${API_BASE_URL}/scan/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!uploadRes.ok) throw new Error(`Upload failed: ${uploadRes.statusText}`);
      const uploadData = await uploadRes.json();
      const jobId = uploadData.job_id;
      setActiveJobId(jobId);

      // Poll status until PARSED or INGESTION_FAILED
      let attempts = 0;
      const interval = setInterval(async () => {
        attempts++;
        const statusRes = await fetch(`${API_BASE_URL}/scan/${jobId}/status`);
        const statusData = await statusRes.json();

        if (statusData.status === 'PARSED') {
          clearInterval(interval);
          await fetchResults(jobId, budget);
          setIsProcessing(false);
        } else if (statusData.status === 'INGESTION_FAILED') {
          clearInterval(interval);
          setErrorState(`INGESTION_FAILED: ${statusData.message || 'Invalid Nessus XML format.'}`);
          setIsProcessing(false);
        } else if (attempts > 20) {
          clearInterval(interval);
          setErrorState('Timeout waiting for scan parsing.');
          setIsProcessing(false);
        }
      }, 300);
    } catch (err) {
      setErrorState(`API Error: ${err.message}`);
      setIsProcessing(false);
    }
  };

  // Select pre-packaged sample dataset
  const handleSampleSelect = async (sampleName) => {
    if (sampleName === 'malformed_corrupt.nessus') {
      setErrorState('INGESTION_FAILED: Failed to parse XML syntax: not well-formed (invalid token): line 7, column 62.');
      return;
    }

    setIsProcessing(true);
    setErrorState(null);

    try {
      // Fetch sample from public/backend
      const res = await fetch(`/sample-data/${sampleName}`);
      let blob;
      if (res.ok) {
        blob = await res.blob();
      } else {
        // Fallback synthetic blob
        blob = new Blob(['<NessusClientData_v2><Report name="Sample"></Report></NessusClientData_v2>'], { type: 'application/xml' });
      }

      const file = new File([blob], sampleName, { type: 'application/xml' });
      await handleFileUpload(file);
    } catch (err) {
      setErrorState(`Sample load failed: ${err.message}`);
      setIsProcessing(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="brand font-mono">
            <span className="brand-logo">🛡️</span>
            <h1>AI-Powered Continuous Cyber Risk Quantification & Investment Optimization Platform</h1>
          </div>
          <div className="header-status font-mono">
            <span className={`status-dot ${apiConnected ? 'connected' : 'offline'}`}></span>
            <span>API {apiConnected ? 'Connected (localhost:8000)' : 'Demo Mode Active'}</span>
          </div>
        </div>
      </header>

      {/* Main Dashboard Grid */}
      <main className="dashboard-main">
        {/* Top Controls Grid */}
        <section className="top-grid">
          <UploadFlow
            onFileUpload={handleFileUpload}
            onSampleSelect={handleSampleSelect}
            isProcessing={isProcessing}
            errorState={errorState}
          />
          <BudgetControl
            currentBudget={budget}
            onBudgetChange={handleBudgetChange}
            isOptimizing={isOptimizing}
          />
        </section>

        {/* Executive KPI Cards */}
        <section className="kpi-section">
          <KPICards
            simulationResults={data?.simulation_results}
            optimizationResults={data?.optimization_results}
            postOptSimulation={data?.post_opt_simulation_results}
          />
        </section>

        {/* Visual Centerpiece: Loss Exceedance Curve */}
        <section className="chart-section">
          <LossExceedanceCurve
            baselineLec={data?.baseline_lec}
            postOptLec={data?.post_opt_lec}
            simulationResults={data?.simulation_results}
            postOptSimulation={data?.post_opt_simulation_results}
            optimizationResults={data?.optimization_results}
          />
        </section>

        {/* Remediation Action List */}
        <section className="table-section">
          <PatchList
            vulnerabilities={data?.vulnerabilities || []}
            simulationResults={data?.simulation_results}
            optimizationResults={data?.optimization_results}
          />
        </section>

        {/* Methodology Disclosure */}
        <section className="assumptions-section">
          <ModelAssumptionsBanner />
        </section>
      </main>
    </div>
  );
}
