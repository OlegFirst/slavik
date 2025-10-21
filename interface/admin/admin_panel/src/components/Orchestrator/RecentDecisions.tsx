/**
 * Recent Decisions Component
 * ===========================
 * Displays recent orchestrator decisions
 */

import React from 'react';
import { Brain, ArrowUpRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { OrchestratorStats } from '@/services/orchestrator-api';

interface RecentDecisionsProps {
  stats?: OrchestratorStats;
  isLoading: boolean;
}

export const RecentDecisions: React.FC<RecentDecisionsProps> = ({ stats, isLoading }) => {
  const totalDecisions = stats?.total_decisions || 0;
  const byAction = stats?.by_action || {};

  const getActionColor = (action: string) => {
    if (action.includes('AUTO_RESOLVE')) return 'bg-green-500';
    if (action.includes('DELEGATE')) return 'bg-blue-500';
    if (action.includes('ESCALATE')) return 'bg-orange-500';
    if (action.includes('EMERGENCY')) return 'bg-red-500';
    return 'bg-gray-500';
  };

  const formatActionName = (action: string) => {
    return action
      .replace('ActionType.', '')
      .replace(/_/g, ' ')
      .toLowerCase()
      .split(' ')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-medium">Decision Summary</CardTitle>
        <Brain className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-sm text-muted-foreground">Loading...</div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-baseline gap-2">
              <div className="text-2xl font-bold">{totalDecisions}</div>
              <div className="text-xs text-muted-foreground">total decisions</div>
            </div>
            <div className="space-y-2">
              {Object.entries(byAction)
                .sort(([, a], [, b]) => (b as number) - (a as number))
                .slice(0, 5)
                .map(([action, count]) => (
                  <div key={action} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge className={getActionColor(action)} variant="outline">
                        {formatActionName(action)}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-sm font-medium">{count}</span>
                      <ArrowUpRight className="h-3 w-3 text-muted-foreground" />
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
