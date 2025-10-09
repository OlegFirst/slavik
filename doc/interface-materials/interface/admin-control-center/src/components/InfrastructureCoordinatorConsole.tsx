/**
 * Infrastructure Coordinator Console
 *
 * Управление Infrastructure Coordinator:
 * - EventBus мониторинг и управление
 * - Health Monitor статус
 * - Auto-Recovery действия
 * - Resource Optimization рекомендации
 * - Governance Layer (Decision Center) интеграция
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Zap,
  Server,
  Network,
  TrendingUp,
  Settings,
  Play,
  Square,
  GitBranch,
  MessageSquare,
  Shield
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { Separator } from './ui/separator';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { ScrollArea } from './ui/scroll-area';
import coordinatorService from '../services/infrastructure-coordinator';

export function InfrastructureCoordinatorConsole() {
  const queryClient = useQueryClient();
  const [selectedTab, setSelectedTab] = useState('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);

  // ============================================================================
  // Data Fetching
  // ============================================================================

  const { data: health, error: healthError } = useQuery({
    queryKey: ['coordinator', 'health'],
    queryFn: () => coordinatorService.getHealth(),
    refetchInterval: autoRefresh ? 5000 : false,
  });

  const { data: stats } = useQuery({
    queryKey: ['coordinator', 'stats'],
    queryFn: () => coordinatorService.getStats(),
    refetchInterval: autoRefresh ? 10000 : false,
  });

  const { data: servicesHealth = [] } = useQuery({
    queryKey: ['coordinator', 'services'],
    queryFn: () => coordinatorService.getServicesHealth(),
    refetchInterval: autoRefresh ? 5000 : false,
  });

  const { data: recoveryActions = [] } = useQuery({
    queryKey: ['coordinator', 'recovery'],
    queryFn: () => coordinatorService.getRecoveryActions(50),
    refetchInterval: autoRefresh ? 5000 : false,
  });

  const { data: recommendations = [] } = useQuery({
    queryKey: ['coordinator', 'recommendations'],
    queryFn: () => coordinatorService.getOptimizationRecommendations(),
    refetchInterval: autoRefresh ? 10000 : false,
  });

  const { data: eventBusStats } = useQuery({
    queryKey: ['coordinator', 'eventbus'],
    queryFn: () => coordinatorService.getEventBusStats(),
    refetchInterval: autoRefresh ? 5000 : false,
  });

  // ============================================================================
  // Mutations
  // ============================================================================

  const triggerRecoveryMutation = useMutation({
    mutationFn: ({ service, strategy }: { service: string; strategy: string }) =>
      coordinatorService.triggerRecovery(service, strategy),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coordinator'] });
    },
  });

  const applyOptimizationMutation = useMutation({
    mutationFn: (recommendationId: string) =>
      coordinatorService.applyOptimization(recommendationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coordinator'] });
    },
  });

  // ============================================================================
  // Render Helpers
  // ============================================================================

  const getHealthBadge = (status: string) => {
    const colors: Record<string, string> = {
      healthy: 'bg-green-500',
      unhealthy: 'bg-red-500',
      unknown: 'bg-gray-500',
    };
    return colors[status] || colors.unknown;
  };

  const formatTimestamp = (ts: string) => {
    return new Date(ts).toLocaleString();
  };

  const getCoordinatorStatus = () => {
    if (healthError) return { color: 'red', label: 'ERROR', icon: AlertTriangle };
    if (!health) return { color: 'gray', label: 'LOADING', icon: RefreshCw };
    if (health.components.eventbus && health.components.health_monitor)
      return { color: 'green', label: 'RUNNING', icon: CheckCircle };
    return { color: 'yellow', label: 'DEGRADED', icon: AlertTriangle };
  };

  const status = getCoordinatorStatus();

  // ============================================================================
  // Main Render
  // ============================================================================

  if (healthError) {
    return (
      <div className="p-8">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Infrastructure Coordinator Unavailable</AlertTitle>
          <AlertDescription>
            Failed to connect to coordinator on port 9092.
            <br />
            Error: {(healthError as Error).message}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Network className="h-8 w-8 text-purple-600" />
            Infrastructure Coordinator Console
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            EventBus | Health Monitor | Auto-Recovery | Resource Optimizer | Governance
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Auto-refresh</label>
            <Button
              variant={autoRefresh ? "default" : "outline"}
              size="sm"
              onClick={() => setAutoRefresh(!autoRefresh)}
            >
              <RefreshCw className={`h-4 w-4 ${autoRefresh ? 'animate-spin' : ''}`} />
            </Button>
          </div>

          <Badge
            variant={status.color === 'green' ? 'default' : 'destructive'}
            className="flex items-center gap-2 px-4 py-2 text-base"
          >
            <status.icon className="h-5 w-5" />
            {status.label}
          </Badge>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Services</CardTitle>
            <Server className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{health?.registered_services || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Monitored</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recovery</CardTitle>
            <Zap className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {stats?.recovery_successes || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {stats?.recovery_failures || 0} failed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Optimizations</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.optimizations_applied || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Applied</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">EventBus</CardTitle>
            <MessageSquare className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {eventBusStats?.total_events_published || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">Events</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Escalations</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {stats?.escalations_triggered || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">Triggered</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">
            <Activity className="h-4 w-4 mr-2" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="services">
            <Server className="h-4 w-4 mr-2" />
            Services
          </TabsTrigger>
          <TabsTrigger value="recovery">
            <Zap className="h-4 w-4 mr-2" />
            Recovery
          </TabsTrigger>
          <TabsTrigger value="optimization">
            <TrendingUp className="h-4 w-4 mr-2" />
            Optimization
          </TabsTrigger>
          <TabsTrigger value="eventbus">
            <Network className="h-4 w-4 mr-2" />
            EventBus
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Components Status */}
            <Card>
              <CardHeader>
                <CardTitle>Components Status</CardTitle>
                <CardDescription>Infrastructure Coordinator Components</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {health && Object.entries(health.components).map(([name, active]) => (
                  <div key={name} className="flex justify-between items-center">
                    <span className="text-sm font-medium capitalize">{name.replace('_', ' ')}</span>
                    <Badge variant={active ? "default" : "destructive"}>
                      {active ? 'ACTIVE' : 'INACTIVE'}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Statistics */}
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
                <CardDescription>Coordinator performance</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600">Health Checks</p>
                  <p className="text-2xl font-bold">{stats?.health_checks_total || 0}</p>
                </div>
                <Separator />
                <div>
                  <p className="text-sm text-gray-600">Avg Recovery Time</p>
                  <p className="text-2xl font-bold">
                    {stats?.avg_recovery_time_seconds?.toFixed(1) || '0'}s
                  </p>
                </div>
                <Separator />
                <div>
                  <p className="text-sm text-gray-600">Recovery Success Rate</p>
                  <p className="text-2xl font-bold">
                    {stats?.recovery_attempts_total
                      ? `${((stats.recovery_successes / stats.recovery_attempts_total) * 100).toFixed(1)}%`
                      : '0%'}
                  </p>
                  <Progress
                    value={stats?.recovery_attempts_total
                      ? (stats.recovery_successes / stats.recovery_attempts_total) * 100
                      : 0}
                    className="mt-2"
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Services Tab */}
        <TabsContent value="services" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Monitored Services Health</CardTitle>
              <CardDescription>{servicesHealth.length} services being monitored</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {servicesHealth.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">No services registered</p>
                ) : (
                  servicesHealth.map((service) => (
                    <div
                      key={service.service_name}
                      className="p-4 border rounded-lg flex items-center justify-between"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <div className={`w-3 h-3 rounded-full ${getHealthBadge(service.status)}`} />
                          <span className="font-medium">{service.service_name}</span>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-gray-600">
                          <span>Response: {service.response_time_ms}ms</span>
                          <span>Failures: {service.consecutive_failures}</span>
                          <span>Last check: {formatTimestamp(service.last_check)}</span>
                        </div>
                      </div>
                      <Badge variant={service.status === 'healthy' ? 'default' : 'destructive'}>
                        {service.status.toUpperCase()}
                      </Badge>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Recovery Tab */}
        <TabsContent value="recovery" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recovery Actions History</CardTitle>
              <CardDescription>Recent auto-recovery attempts</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[600px]">
                <div className="space-y-2">
                  {recoveryActions.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">No recovery actions yet</p>
                  ) : (
                    recoveryActions.map((action) => (
                      <div key={action.id} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Zap className="h-4 w-4 text-yellow-600" />
                            <span className="font-medium">{action.service_name}</span>
                            <Badge variant="outline">{action.strategy}</Badge>
                          </div>
                          <Badge
                            variant={action.status === 'success' ? 'default' :
                                   action.status === 'failed' ? 'destructive' : 'secondary'}
                          >
                            {action.status.toUpperCase()}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-gray-600">
                          <span>Attempt #{action.attempt_number}</span>
                          <span>Approved: {action.decision_approved ? 'Yes' : 'No'}</span>
                          <span>{formatTimestamp(action.timestamp)}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Optimization Tab */}
        <TabsContent value="optimization" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Optimization Recommendations</CardTitle>
              <CardDescription>Resource optimization suggestions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recommendations.length === 0 ? (
                  <div className="text-center py-8">
                    <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
                    <p className="text-lg font-medium">All Systems Optimal</p>
                    <p className="text-sm text-gray-500">No optimization recommendations</p>
                  </div>
                ) : (
                  recommendations.map((rec) => (
                    <div
                      key={rec.id}
                      className={`p-4 border rounded-lg ${
                        rec.priority === 'critical' ? 'border-red-500 bg-red-50' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <TrendingUp className="h-4 w-4 text-purple-600" />
                            <span className="font-medium">{rec.service_name}</span>
                            <Badge variant="outline">{rec.resource_type}</Badge>
                            <Badge
                              variant={rec.priority === 'critical' ? 'destructive' : 'secondary'}
                            >
                              {rec.priority}
                            </Badge>
                          </div>
                          <p className="text-sm mb-2">{rec.recommendation}</p>
                          <div className="flex items-center gap-4 text-xs text-gray-600">
                            <span>Usage: {rec.current_usage}%</span>
                            <span>Threshold: {rec.threshold}%</span>
                            <span>{formatTimestamp(rec.timestamp)}</span>
                          </div>
                        </div>
                        {!rec.auto_applied && (
                          <Button
                            size="sm"
                            onClick={() => applyOptimizationMutation.mutate(rec.id)}
                          >
                            Apply
                          </Button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* EventBus Tab */}
        <TabsContent value="eventbus" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>EventBus Statistics</CardTitle>
                <CardDescription>Real-time event bus metrics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600">Backend</p>
                  <p className="text-2xl font-bold uppercase">{eventBusStats?.backend || 'N/A'}</p>
                </div>
                <Separator />
                <div>
                  <p className="text-sm text-gray-600">Connection</p>
                  <Badge variant={eventBusStats?.connected ? 'default' : 'destructive'}>
                    {eventBusStats?.connected ? 'CONNECTED' : 'DISCONNECTED'}
                  </Badge>
                </div>
                <Separator />
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Events Published</p>
                    <p className="text-xl font-bold">{eventBusStats?.total_events_published || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Subscriptions</p>
                    <p className="text-xl font-bold">{eventBusStats?.total_subscriptions || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Active Consumers</p>
                    <p className="text-xl font-bold">{eventBusStats?.active_consumers || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Queue Depth</p>
                    <p className="text-xl font-bold">{eventBusStats?.queue_depth || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>EventBus Management</CardTitle>
                <CardDescription>Control and monitoring</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert>
                  <Network className="h-4 w-4" />
                  <AlertTitle>EventBus Integration</AlertTitle>
                  <AlertDescription>
                    EventBus является центральной шиной событий для всей платформы.
                    Используется для координации между сервисами.
                  </AlertDescription>
                </Alert>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <MessageSquare className="h-4 w-4 mr-2" />
                    View Events
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Clear Queue
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <div className="text-center text-sm text-gray-500 pt-6 border-t">
        <p>
          Infrastructure Coordinator Console |
          Uptime: {health?.uptime_seconds ? `${Math.floor(health.uptime_seconds / 60)}m` : '0m'} |
          Status: <span className="font-medium text-green-600">
            {health?.components.eventbus ? 'OPERATIONAL' : 'UNAVAILABLE'}
          </span>
        </p>
      </div>
    </div>
  );
}

export default InfrastructureCoordinatorConsole;
