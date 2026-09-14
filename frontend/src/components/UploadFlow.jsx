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
    <div className="upload-card">
      <div className="upload-header">
        <h3>Nessus Vulnerability Scan Ingestion</h3>
        <p className="upload-subtitle">
          Upload a real .nessus XML file to execute continuous ingestion, local database CVE enrichment, FAIR calibration, vectorized Monte Carlo, and PuLP optimization.
        </p>
      </div>

      <div className="upload-dropzone" onClick={() => fileInputRef.current?.click()}>
        <input
          type="file"
          ref={fileInputRef}
          accept=".nessus,.xml"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <div className="dropzone-content">
          <div className="upload-icon">📄</div>
          <p className="dropzone-text">
            <strong>Click to upload</strong> or drag & drop a <code>.nessus</code> XML scan file
          </p>
          <p className="dropzone-hint">Supports Nessus Client Data v2 XML format</p>
        </div>
      </div>

      <div className="sample-scans-section">
        <span className="sample-label font-mono">Quick Run Demo Datasets:</span>
        <div className="sample-buttons">
          <button
            type="button"
            className="sample-btn btn-primary"
            onClick={() => onSampleSelect('enterprise_perimeter_scan.nessus')}
            disabled={isProcessing}
          >
            🏢 Enterprise Perimeter Scan (5 CVEs)
          </button>

          <button
            type="button"
            className="sample-btn btn-secondary"
            onClick={() => onSampleSelect('internal_services_scan.nessus')}
            disabled={isProcessing}
          >
            🔒 Internal Services Scan
          </button>

          <button
            type="button"
            className="sample-btn btn-danger"
            onClick={() => onSampleSelect('malformed_corrupt.nessus')}
            disabled={isProcessing}
          >
            ⚠️ Malformed Scan (Fail-Soft Test)
          </button>
        </div>
      </div>

      {errorState && (
        <div className="error-banner">
          <span className="error-title font-mono">⚠️ Pipeline Exception Captured (Fail-Soft):</span>
          <p className="error-message">{errorState}</p>
        </div>
      )}
    </div>
  );
}
