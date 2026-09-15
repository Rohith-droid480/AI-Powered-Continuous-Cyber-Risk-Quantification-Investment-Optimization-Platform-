import React, { useRef } from 'react';

export default function UploadFlow({ onFileUpload, onSampleSelect, isProcessing, errorState }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileUpload(file);
    }
  };

  return (
    <div className="view-card upload-card font-sans">
      <div className="card-header">
        <div>
          <h3 className="card-title font-mono">
            <span className="title-icon">📡</span> Nessus Vulnerability Scan Ingestion
          </h3>
          <p className="card-subtitle">
            Upload a real <code>.nessus</code> XML scan to execute continuous ingestion, CVE threat enrichment, FAIR calibration, Monte Carlo simulation, and PuLP optimization.
          </p>
        </div>
        <span className="status-badge font-mono selected">Layer 1 Pipeline</span>
      </div>

      {/* Drag & Drop Zone */}
      <div className="upload-dropzone" onClick={() => fileInputRef.current?.click()}>
        <input
          type="file"
          ref={fileInputRef}
          accept=".nessus,.xml"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <div className="dropzone-content">
          <div className="upload-icon-box">
            <span className="upload-icon">📄</span>
          </div>
          <p className="dropzone-text">
            <strong>Click to upload</strong> or drag & drop a <code>.nessus</code> XML scan file
          </p>
          <p className="dropzone-hint font-mono">Supports Nessus Client Data v2 XML format</p>
        </div>
      </div>

      {/* Quick Run Presets Bar */}
      <div className="sample-scans-section">
        <div className="sample-header font-mono">
          <span className="pulse-dot"></span>
          <span>QUICK RUN DEMO DATASETS</span>
        </div>

        <div className="sample-buttons-grid">
          <button
            type="button"
            className="sample-btn primary font-mono"
            onClick={() => onSampleSelect('enterprise_perimeter_scan.nessus')}
            disabled={isProcessing}
          >
            <span className="btn-icon">🏢</span>
            <div className="btn-text">
              <span className="btn-title">Enterprise Perimeter Scan</span>
              <span className="btn-sub">5 Vulnerabilities (Log4j, Zerologon, etc.)</span>
            </div>
            <span className="btn-tag font-mono">Recommended</span>
          </button>

          <button
            type="button"
            className="sample-btn secondary font-mono"
            onClick={() => onSampleSelect('internal_services_scan.nessus')}
            disabled={isProcessing}
          >
            <span className="btn-icon">🔒</span>
            <div className="btn-text">
              <span className="btn-title">Internal Services Scan</span>
              <span className="btn-sub">Core Infrastructure Scan</span>
            </div>
            <span className="btn-tag font-mono">Sample</span>
          </button>

          <button
            type="button"
            className="sample-btn danger font-mono"
            onClick={() => onSampleSelect('malformed_corrupt.nessus')}
            disabled={isProcessing}
          >
            <span className="btn-icon">⚠️</span>
            <div className="btn-text">
              <span className="btn-title">Malformed Scan</span>
              <span className="btn-sub">Fail-Soft Pipeline Test</span>
            </div>
            <span className="btn-tag danger font-mono">Test Error</span>
          </button>
        </div>
      </div>

      {errorState && (
        <div className="error-banner animate-fadeIn font-mono">
          <div className="error-content">
            <span className="error-icon">⚠️</span>
            <div className="error-text">
              <strong>Pipeline Alert:</strong> {errorState}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
