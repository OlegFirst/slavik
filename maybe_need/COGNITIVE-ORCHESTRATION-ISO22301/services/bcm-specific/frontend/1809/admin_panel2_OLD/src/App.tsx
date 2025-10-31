import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import BCMAdminControlCenter from '@/components/BCMAdminControlCenter';
import RealDataDashboard from '@/components/RealDataDashboard';
import AIConfiguration from '@/pages/AIConfiguration';
import DigitalTwinDashboard from '@/components/DigitalTwin/DigitalTwinDashboard';
import PersonalTwinManager from '@/components/DigitalTwin/PersonalTwinManager';
import DataCollectionMonitor from '@/components/DigitalTwin/DataCollectionMonitor';
import PackageManager from '@/components/DigitalTwin/PackageManager';
import SystemHealthMonitor from '@/components/DigitalTwin/SystemHealthMonitor';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '@/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000, // 30 seconds
      cacheTime: 300000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<BCMAdminControlCenter />} />
          <Route path="/real-data" element={<RealDataDashboard />} />
          <Route path="/ai-configuration" element={<AIConfiguration />} />
          <Route path="/digital-twin" element={<DigitalTwinDashboard />} />
          <Route path="/digital-twin/dashboard" element={<DigitalTwinDashboard />} />
          <Route path="/digital-twin/personal" element={<PersonalTwinManager />} />
          <Route path="/digital-twin/data-collection" element={<DataCollectionMonitor />} />
          <Route path="/digital-twin/packages" element={<PackageManager />} />
          <Route path="/digital-twin/health" element={<SystemHealthMonitor />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
