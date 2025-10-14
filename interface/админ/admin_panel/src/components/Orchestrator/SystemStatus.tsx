/**
 * System Status Component
 * ========================
 * Shows health of orchestrator components
 */

import React from 'react';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { HealthStatus } from '@/services/orchestrator-api';

interface SystemStatusProps {
  health?: HealthStatus;
  isLoading: boolean;
}

export const SystemStatus: React.FC<SystemStatusProps> = ({ health, isLoading }) => {
  const components = health?.components || {
    event_bus: false,
    service_registry: false,
    decision_center: false,
    crisis_coordinator: false,
    pdca_engine: false,
  };

  const componentLabels = {
    event_bus: 'Event Bus',
    service_registry: 'Service Registry',
    decision_center: 'Decision Center',
    crisis_coordinator: 'Crisis Coordinator',
    pdca_engine: 'PDCA Engine',
  };

  const getIcon = (status: boolean) => {
    if (isLoading) return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
    return status ? (
      <CheckCircle className="w-4 h-4 text-green-500" />
    ) : (
      <XCircle className="w-4 h-4 text-red-500" />
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">System Components</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {Object.entries(components).map(([key, status]) => (
            <div key={key} className="flex items-center justify-between">
              <span className="text-sm">{componentLabels[key as keyof typeof componentLabels]}</span>
              <div className="flex items-center gap-2">
                {getIcon(status)}
                <span className={`text-xs ${status ? 'text-green-600' : 'text-red-600'}`}>
                  {status ? 'Online' : 'Offline'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
