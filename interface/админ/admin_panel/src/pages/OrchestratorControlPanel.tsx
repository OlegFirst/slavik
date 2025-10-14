/**
 * Orchestrator Control Panel
 * ===========================
 * Main page for AI Orchestrator monitoring and management
 */

import React from 'react';
import { OrchestratorHeader } from '@/components/Orchestrator/OrchestratorHeader';
import { SystemStatus } from '@/components/Orchestrator/SystemStatus';
import { PerformanceMetrics } from '@/components/Orchestrator/PerformanceMetrics';
import { ActiveCrises } from '@/components/Orchestrator/ActiveCrises';
import { RecentDecisions } from '@/components/Orchestrator/RecentDecisions';
import { QuickActions } from '@/components/Orchestrator/QuickActions';
import { ServiceHealthGrid } from '@/components/Orchestrator/ServiceHealthGrid';
import { AIExpertsDelegation } from '@/components/Orchestrator/AIExpertsDelegation';
import { useOrchestratorHealth, useOrchestratorStats } from '@/hooks/useOrchestratorHealth';

export const OrchestratorControlPanel: React.FC = () => {
  const { data: health, isLoading: healthLoading } = useOrchestratorHealth(5000);
  const { data: stats, isLoading: statsLoading } = useOrchestratorStats(10000);

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <OrchestratorHeader health={health} isLoading={healthLoading} />

        {/* Performance Metrics */}
        <PerformanceMetrics stats={stats} isLoading={statsLoading} />

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            <SystemStatus health={health} isLoading={healthLoading} />
            <QuickActions />
          </div>

          {/* Middle Column */}
          <div className="space-y-6">
            <ActiveCrises stats={stats} isLoading={statsLoading} />
            <AIExpertsDelegation stats={stats} isLoading={statsLoading} />
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            <RecentDecisions stats={stats} isLoading={statsLoading} />
          </div>
        </div>

        {/* Service Health Grid */}
        <ServiceHealthGrid stats={stats} isLoading={statsLoading} />
      </div>
    </div>
  );
};

export default OrchestratorControlPanel;
