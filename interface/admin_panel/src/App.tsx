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
import BCMUnifiedWorkspace from '@/components/BCMUnifiedWorkspace';
import CentralizedArchitectureMonitor from '@/components/CentralizedArchitectureMonitor';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { KeycloakAuthProvider } from '@/auth/KeycloakAuthProvider';
import '@/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000, // 30 seconds
      gcTime: 300000, // 5 minutes (was cacheTime in v4, now gcTime in v5)
    },
  },
});

function App() {
  return (
    <KeycloakAuthProvider>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            <Route path="/" element={<BCMUnifiedWorkspace />} />
            <Route path="/dashboard" element={<RealDataDashboard />} />
            <Route path="/admin" element={<BCMAdminControlCenter />} />
            <Route path="/architecture" element={<CentralizedArchitectureMonitor />} />
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
    </KeycloakAuthProvider>
  );
}

export default App;
