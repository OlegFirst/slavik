/**
 * Active Crises Component
 * ========================
 * Displays active crisis situations
 */

import React from 'react';
import { AlertTriangle, Shield } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { OrchestratorStats } from '@/services/orchestrator-api';

interface ActiveCrisesProps {
  stats?: OrchestratorStats;
  isLoading: boolean;
}

export const ActiveCrises: React.FC<ActiveCrisesProps> = ({ stats, isLoading }) => {
  const crisisStats = stats?.crisis_stats;
  const activeCrises = crisisStats?.active_crisis_ids || [];
  const crisisByLevel = crisisStats?.by_level || {};

  const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'MINOR':
        return 'bg-blue-500';
      case 'MAJOR':
        return 'bg-yellow-500';
      case 'CRITICAL':
        return 'bg-orange-500';
      case 'CATASTROPHIC':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-medium">Active Crises</CardTitle>
        <AlertTriangle className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-sm text-muted-foreground">Loading...</div>
        ) : activeCrises.length === 0 ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Shield className="h-4 w-4 text-green-500" />
            <span>No active crises</span>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="text-2xl font-bold">{activeCrises.length}</div>
            <div className="space-y-2">
              {Object.entries(crisisByLevel).map(([level, count]) => (
                <div key={level} className="flex items-center justify-between">
                  <Badge className={getLevelColor(level)}>{level}</Badge>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
            <div className="text-xs text-muted-foreground">
              {activeCrises.slice(0, 3).map((id) => (
                <div key={id} className="truncate">
                  • {id}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
