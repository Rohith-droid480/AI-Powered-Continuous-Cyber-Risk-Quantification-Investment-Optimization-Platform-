import React from 'react';
import UploadFlow from '../UploadFlow';
import LayerPipeline from '../common/LayerPipeline';

export default function ScanIngestionView({
  onFileUpload,
  onSampleSelect,
  isProcessing,
  activeJobId,
  apiConnected
}) {
  return (
    <div className="scan-ingestion-view animate-fadeIn">
      {/* Upload Flow Box */}
      <UploadFlow
        onFileUpload={onFileUpload}
        onSampleSelect={onSampleSelect}
        isProcessing={isProcessing}
        activeJobId={activeJobId}
        apiConnected={apiConnected}
      />

      {/* Layer 1 - Layer 6 Interactive Architecture Pipeline */}
      <LayerPipeline currentLayer={6} />
    </div>
  );
}
