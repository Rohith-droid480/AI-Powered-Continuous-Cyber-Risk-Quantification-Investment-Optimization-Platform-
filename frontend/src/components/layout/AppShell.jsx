import React from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

export default function AppShell({
  activeTab,
  setActiveTab,
  apiConnected,
  budget,
  data,
  children
}) {
  return (
    <div className="app-shell-layout">
      {/* Left Persistent Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        apiConnected={apiConnected}
        activeScanName={data?.job_id ? `Scan: ${data.job_id}` : 'enterprise_perimeter_scan.nessus'}
      />

      {/* Main Content Area */}
      <div className="app-main-viewport">
        {/* Top Header Bar */}
        <TopBar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          apiConnected={apiConnected}
          budget={budget}
          data={data}
        />

        {/* View Component Container */}
        <main className="app-view-container">
          {children}
        </main>
      </div>
    </div>
  );
}
