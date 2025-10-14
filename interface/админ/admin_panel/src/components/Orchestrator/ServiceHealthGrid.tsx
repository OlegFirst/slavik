/**
 * Service Health Grid Component
 * ==============================
 * Displays health status of all registered services
 */

import React from 'react';
import { Server, CheckCircle, XCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { OrchestratorStats } from '@/services/orchestrator-api';

interface ServiceHealthGridProps {
  stats?: OrchestratorStats;
  isLoading: boolean;
}

export const ServiceHealthGrid: React.FC<ServiceHealthGridProps> = ({ stats, isLoading }) => {
  const services = stats?.service_registry?.services || [];
  const healthyCount = stats?.service_registry?.healthy_services || 0;
  const totalCount = stats?.service_registry?.total_services || 0;

  const getStatusIcon = (status: string) => {
    return status === 'healthy' ? (
      <CheckCircle className="h-4 w-4 text-green-500" />
    ) : (
      <XCircle className="h-4 w-4 text-red-500" />
    );
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-medium">Service Health</CardTitle>
        <div className="flex items-center gap-2">
          <Server className="h-4 w-4 text-muted-foreground" />
          <Badge variant={healthyCount === totalCount ? 'default' : 'destructive'}>
            {healthyCount}/{totalCount} Healthy
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-sm text-muted-foreground">Loading services...</div>
        ) : services.length === 0 ? (
          <div className="text-sm text-muted-foreground">No services registered</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {services.map((service) => (
              <div
                key={service.name}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div className="flex items-center gap-2">
                  {getStatusIcon(service.status)}
                  <div>
                    <div className="text-sm font-medium">{service.name}</div>
                    <div className="text-xs text-muted-foreground truncate max-w-[150px]">
                      {service.url}
                    </div>
                  </div>
                </div>
                <Badge
                  variant={service.status === 'healthy' ? 'default' : 'destructive'}
                  className="text-xs"
                >
                  {service.status}
                </Badge>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
