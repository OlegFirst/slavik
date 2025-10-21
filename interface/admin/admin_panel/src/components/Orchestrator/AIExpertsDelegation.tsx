/**
 * AI Experts Delegation Component
 * ================================
 * Shows delegation statistics to AI Experts
 */

import React from 'react';
import { Users } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import type { OrchestratorStats } from '@/services/orchestrator-api';

interface AIExpertsDelegationProps {
  stats?: OrchestratorStats;
  isLoading: boolean;
}

export const AIExpertsDelegation: React.FC<AIExpertsDelegationProps> = ({ stats, isLoading }) => {
  const delegationStats = stats?.delegation_stats;
  const totalDelegations = delegationStats?.total_delegations || 0;
  const bySpecialist = delegationStats?.by_specialist || {};

  // Filter AI Experts (those starting with 'ai-expert-')
  const aiExperts = Object.entries(bySpecialist).filter(([name]) =>
    name.startsWith('ai-expert-')
  );

  const formatExpertName = (name: string) => {
    return name
      .replace('ai-expert-', '')
      .replace(/-/g, ' ')
      .split(' ')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getProgressPercentage = (count: number) => {
    if (totalDelegations === 0) return 0;
    return (count / totalDelegations) * 100;
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-medium">AI Experts Delegation</CardTitle>
        <Users className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-sm text-muted-foreground">Loading...</div>
        ) : aiExperts.length === 0 ? (
          <div className="text-sm text-muted-foreground">No delegations to AI Experts yet</div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-baseline gap-2">
              <div className="text-2xl font-bold">{totalDelegations}</div>
              <div className="text-xs text-muted-foreground">total delegations</div>
            </div>
            <div className="space-y-3">
              {aiExperts.map(([name, count]) => (
                <div key={name} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{formatExpertName(name)}</span>
                    <span className="text-muted-foreground">{count}</span>
                  </div>
                  <Progress value={getProgressPercentage(count as number)} className="h-2" />
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
