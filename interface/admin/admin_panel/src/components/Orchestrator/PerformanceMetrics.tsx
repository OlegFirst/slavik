/**
 * Performance Metrics Component
 * ==============================
 * Displays key performance indicators
 */

import React from 'react';
import { TrendingUp, TrendingDown, Zap, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { OrchestratorStats } from '@/services/orchestrator-api';

interface PerformanceMetricsProps {
  stats?: OrchestratorStats;
  isLoading: boolean;
}

export const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ stats, isLoading }) => {
  const metrics = [
    {
      title: 'Decision Latency',
      value: stats ? `${stats.avg_latency_ms.toFixed(1)}ms` : '-',
      icon: Zap,
      trend: stats && stats.avg_latency_ms < 50 ? 'up' : 'down',
      target: '< 50ms',
    },
    {
      title: 'Auto-Resolution Rate',
      value: stats ? `${(stats.auto_resolution_rate * 100).toFixed(1)}%` : '-',
      icon: TrendingUp,
      trend: stats && stats.auto_resolution_rate > 0.7 ? 'up' : 'down',
      target: '> 70%',
    },
    {
      title: 'Escalation Rate',
      value: stats ? `${(stats.escalation_rate * 100).toFixed(1)}%` : '-',
      icon: AlertCircle,
      trend: stats && stats.escalation_rate < 0.2 ? 'up' : 'down',
      target: '< 20%',
    },
    {
      title: 'Safety Approval',
      value: stats ? `${(stats.safety_approval_rate * 100).toFixed(1)}%` : '-',
      icon: TrendingUp,
      trend: stats && stats.safety_approval_rate > 0.95 ? 'up' : 'down',
      target: '> 95%',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric) => (
        <Card key={metric.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{metric.title}</CardTitle>
            <metric.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '...' : metric.value}
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              {metric.trend === 'up' ? (
                <TrendingUp className="h-3 w-3 text-green-500" />
              ) : (
                <TrendingDown className="h-3 w-3 text-red-500" />
              )}
              <span>Target: {metric.target}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
