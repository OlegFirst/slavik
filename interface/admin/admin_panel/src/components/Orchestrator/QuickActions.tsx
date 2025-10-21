/**
 * Quick Actions Component
 * ========================
 * Action buttons for orchestrator management
 */

import React, { useState } from 'react';
import { RefreshCw, Trash2, Zap } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { orchestratorAPI } from '@/services/orchestrator-api';
import { useToast } from '@/hooks/use-toast';

export const QuickActions: React.FC = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState<string | null>(null);

  const handleTriggerEvolution = async () => {
    setLoading('evolution');
    try {
      await orchestratorAPI.triggerEvolution();
      toast({
        title: 'Evolution Triggered',
        description: 'Evolution cycle started successfully',
      });
    } catch (error) {
      toast({
        title: 'Evolution Failed',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive',
      });
    } finally {
      setLoading(null);
    }
  };

  const handleClearCache = async () => {
    setLoading('cache');
    try {
      await orchestratorAPI.clearCache();
      toast({
        title: 'Cache Cleared',
        description: 'Strategy cache cleared successfully',
      });
    } catch (error) {
      toast({
        title: 'Clear Cache Failed',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive',
      });
    } finally {
      setLoading(null);
    }
  };

  const actions = [
    {
      id: 'evolution',
      title: 'Trigger Evolution',
      description: 'Start evolution cycle',
      icon: Zap,
      onClick: handleTriggerEvolution,
      variant: 'default' as const,
    },
    {
      id: 'cache',
      title: 'Clear Cache',
      description: 'Clear strategy cache',
      icon: Trash2,
      onClick: handleClearCache,
      variant: 'outline' as const,
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {actions.map((action) => (
          <Button
            key={action.id}
            variant={action.variant}
            className="w-full justify-start"
            onClick={action.onClick}
            disabled={loading !== null}
          >
            {loading === action.id ? (
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <action.icon className="mr-2 h-4 w-4" />
            )}
            <div className="flex flex-col items-start">
              <span className="text-sm font-medium">{action.title}</span>
              <span className="text-xs text-muted-foreground">{action.description}</span>
            </div>
          </Button>
        ))}
      </CardContent>
    </Card>
  );
};
