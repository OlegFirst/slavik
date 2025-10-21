/**
 * Orchestrator Header Component
 * ==============================
 */

import React from 'react';
import { Activity, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { HealthStatus } from '@/services/orchestrator-api';

interface OrchestratorHeaderProps {
  health?: HealthStatus;
  isLoading: boolean;
}

export const OrchestratorHeader: React.FC<OrchestratorHeaderProps> = ({ health, isLoading }) => {
  const getStatusIcon = () => {
    if (isLoading) return <Activity className="w-5 h-5 animate-spin text-blue-500" />;
    if (!health) return <XCircle className="w-5 h-5 text-red-500" />;

    switch (health.status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'unhealthy':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusBadge = () => {
    if (isLoading) return <Badge variant="outline">Connecting...</Badge>;
    if (!health) return <Badge variant="destructive">Offline</Badge>;

    switch (health.status) {
      case 'healthy':
        return <Badge className="bg-green-500">Operational</Badge>;
      case 'degraded':
        return <Badge className="bg-yellow-500">Degraded</Badge>;
      case 'unhealthy':
        return <Badge variant="destructive">Unhealthy</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  return (
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-4">
        {getStatusIcon()}
        <div>
          <h1 className="text-3xl font-bold">AI Orchestrator Control Panel</h1>
          <p className="text-sm text-muted-foreground">
            Intelligent decision-making and crisis coordination
          </p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        {getStatusBadge()}
        {health && (
          <span className="text-xs text-muted-foreground">
            Last updated: {new Date(health.timestamp).toLocaleTimeString()}
          </span>
        )}
      </div>
    </div>
  );
};
