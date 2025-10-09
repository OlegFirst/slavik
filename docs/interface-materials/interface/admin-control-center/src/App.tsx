import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AIPlatformControlCenter from '@/components/AIPlatformControlCenter';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '@/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000, // 30 seconds
      gcTime: 300000, // 5 minutes
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* AI Platform Control Center - Full administrative portal */}
          <Route path="/*" element={<AIPlatformControlCenter />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
