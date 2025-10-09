/**
 * Orchestrator Performance Dashboard
 *
 * Real-time monitoring dashboard for AI Orchestrator performance.
 * Displays golden metrics, agent utilization, LLM performance, and alerts.
 *
 * Features:
 * - Golden metrics (throughput, latency, success rate)
 * - Agent utilization charts
 * - LLM performance tracking
 * - Resource monitoring
 * - Active alerts
 * - Cost tracking
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Activity,
  TrendingUp,
  Zap,
  CheckCircle,
  AlertTriangle,
  Clock,
  DollarSign,
  Cpu,
  BarChart3,
  Bot,
  Brain,
  Server,
  Database,
  AlertCircle,
  Info
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

// ============================================================================
// TYPES
// ============================================================================

interface GoldenMetrics {
  throughput_tpm: number;
  p95_latency_seconds: number;
  success_rate_percent: number;
  active_tasks: number;
}

interface AgentStats {
  total_count: number;
  avg_utilization_percent: number;
  active_agents: number;
  top_agents: Array<{
    name: string;
    tasks_completed: number;
    utilization_percent: number;
  }>;
}

interface LLMStats {
  total_calls: number;
  total_tokens: number;
  total_cost: number;
  avg_latency: number;
  by_model: Record<string, any>;
}

interface ResourceStats {
  cpu_percent: number;
  memory_bytes: number;
  memory_percent: number;
}

interface AlertInfo {
  severity: 'critical' | 'warning' | 'info';
  message: string;
  timestamp: string;
}

interface AlertsStats {
  total_active: number;
  critical: number;
  warning: number;
  recent: AlertInfo[];
}

interface DashboardData {
  status: string;
  timestamp: string;
  window_minutes: number;
  golden_metrics: GoldenMetrics;
  performance: {
    total_requests: number;
    avg_latency: number;
    p50_latency: number;
    p99_latency: number;
  };
  tasks: {
    total: number;
    successful: number;
    failed: number;
    success_rate: number;
    total_tokens: number;
    total_cost: number;
    avg_cost: number;
  };
  agents: AgentStats;
  llm: LLMStats;
  resources: ResourceStats;
  alerts: AlertsStats;
  sla: {
    compliance_rate: number;
    violations: number;
  };
}

// ============================================================================
// API CLIENT
// ============================================================================

const ORCHESTRATOR_API = 'http://localhost:8030';

async function fetchDashboardData(windowMinutes: number = 60): Promise<DashboardData> {
  const response = await fetch(`${ORCHESTRATOR_API}/api/v1/monitoring/dashboard?window_minutes=${windowMinutes}`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// ============================================================================
// UTILITY COMPONENTS
// ============================================================================

function MetricCard({
  title,
  value,
  unit,
  icon: Icon,
  trend,
  status
}: {
  title: string;
  value: number | string;
  unit?: string;
  icon: any;
  trend?: 'up' | 'down';
  status?: 'good' | 'warning' | 'critical';
}) {
  const statusColors = {
    good: 'text-green-600',
    warning: 'text-yellow-600',
    critical: 'text-red-600'
  };

  const statusBgColors = {
    good: 'bg-green-50',
    warning: 'bg-yellow-50',
    critical: 'bg-red-50'
  };

  return (
    <Card className={status ? statusBgColors[status] : ''}>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <div className="flex items-baseline gap-2 mt-2">
              <h3 className={`text-2xl font-bold ${status ? statusColors[status] : ''}`}>
                {typeof value === 'number' ? value.toFixed(2) : value}
              </h3>
              {unit && <span className="text-sm text-muted-foreground">{unit}</span>}
            </div>
          </div>
          <div className={`p-3 rounded-full ${status ? statusBgColors[status] : 'bg-primary/10'}`}>
            <Icon className={`w-6 h-6 ${status ? statusColors[status] : 'text-primary'}`} />
          </div>
        </div>
        {trend && (
          <div className="mt-2 flex items-center gap-1 text-sm">
            <TrendingUp className={`w-4 h-4 ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`} />
            <span className="text-muted-foreground">vs. previous window</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function LoadingState() {
  return (
    <div className="flex items-center justify-center h-96">
      <div className="text-center">
        <Activity className="w-12 h-12 animate-spin mx-auto mb-4 text-primary" />
        <p className="text-muted-foreground">Loading orchestrator metrics...</p>
      </div>
    </div>
  );
}

function ErrorState({ error }: { error: Error }) {
  return (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Failed to load orchestrator metrics</AlertTitle>
      <AlertDescription>
        {error.message}
        <br />
        <span className="text-sm">Make sure orchestrator service is running on port 8030</span>
      </AlertDescription>
    </Alert>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function OrchestratorDashboard() {
  const [windowMinutes, setWindowMinutes] = useState(60);

  const { data, isLoading, error, refetch } = useQuery<DashboardData>({
    queryKey: ['orchestrator-dashboard', windowMinutes],
    queryFn: () => fetchDashboardData(windowMinutes),
    refetchInterval: 10000, // Refresh every 10 seconds
    retry: 3,
    retryDelay: 1000
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState error={error as Error} />;
  if (!data || data.status === 'not_initialized') {
    return (
      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>Monitoring Not Initialized</AlertTitle>
        <AlertDescription>
          Orchestrator monitoring system is not yet initialized.
          Performance tracking will be available once the orchestrator is running.
        </AlertDescription>
      </Alert>
    );
  }

  const { golden_metrics, performance, tasks, agents, llm, resources, alerts, sla } = data;

  // Determine status colors
  const getLatencyStatus = (latency: number): 'good' | 'warning' | 'critical' => {
    if (latency < 2) return 'good';
    if (latency < 5) return 'warning';
    return 'critical';
  };

  const getSuccessRateStatus = (rate: number): 'good' | 'warning' | 'critical' => {
    if (rate >= 95) return 'good';
    if (rate >= 90) return 'warning';
    return 'critical';
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Orchestrator Performance</h2>
          <p className="text-muted-foreground">
            Real-time monitoring of AI orchestration system
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline">
            Last updated: {new Date(data.timestamp).toLocaleTimeString()}
          </Badge>
          <select
            value={windowMinutes}
            onChange={(e) => setWindowMinutes(Number(e.target.value))}
            className="px-3 py-2 border rounded-md text-sm"
          >
            <option value={5}>Last 5 min</option>
            <option value={15}>Last 15 min</option>
            <option value={60}>Last 1 hour</option>
            <option value={360}>Last 6 hours</option>
            <option value={1440}>Last 24 hours</option>
          </select>
        </div>
      </div>

      {/* Active Alerts */}
      {alerts.total_active > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>
            {alerts.total_active} Active Alert{alerts.total_active > 1 ? 's' : ''}
          </AlertTitle>
          <AlertDescription>
            <div className="space-y-1 mt-2">
              {alerts.recent.map((alert, idx) => (
                <div key={idx} className="text-sm">
                  <Badge variant={alert.severity === 'critical' ? 'destructive' : 'outline'} className="mr-2">
                    {alert.severity}
                  </Badge>
                  {alert.message}
                </div>
              ))}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Golden Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Throughput"
          value={golden_metrics.throughput_tpm}
          unit="tasks/min"
          icon={Zap}
          status="good"
        />
        <MetricCard
          title="P95 Latency"
          value={golden_metrics.p95_latency_seconds}
          unit="seconds"
          icon={Clock}
          status={getLatencyStatus(golden_metrics.p95_latency_seconds)}
        />
        <MetricCard
          title="Success Rate"
          value={golden_metrics.success_rate_percent}
          unit="%"
          icon={CheckCircle}
          status={getSuccessRateStatus(golden_metrics.success_rate_percent)}
        />
        <MetricCard
          title="Active Tasks"
          value={golden_metrics.active_tasks}
          icon={Activity}
        />
      </div>

      {/* Detailed Metrics Tabs */}
      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="agents">Agents</TabsTrigger>
          <TabsTrigger value="llm">LLM</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
        </TabsList>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Request Performance</CardTitle>
                <CardDescription>Latency percentiles</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>P50 (Median)</span>
                    <span className="font-medium">{performance.p50_latency.toFixed(2)}s</span>
                  </div>
                  <Progress value={Math.min((performance.p50_latency / 5) * 100, 100)} />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>P95</span>
                    <span className="font-medium">{performance.p95_latency.toFixed(2)}s</span>
                  </div>
                  <Progress value={Math.min((performance.p95_latency / 5) * 100, 100)} />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>P99</span>
                    <span className="font-medium">{performance.p99_latency.toFixed(2)}s</span>
                  </div>
                  <Progress value={Math.min((performance.p99_latency / 5) * 100, 100)} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Total Requests</CardTitle>
                <CardDescription>In selected window</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold">{performance.total_requests}</div>
                <p className="text-sm text-muted-foreground mt-2">
                  Avg: {performance.avg_latency.toFixed(2)}s per request
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>SLA Compliance</CardTitle>
                <CardDescription>Service level agreement</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold">{sla.compliance_rate.toFixed(1)}%</div>
                <p className="text-sm text-muted-foreground mt-2">
                  {sla.violations} violation{sla.violations !== 1 ? 's' : ''}
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Agents Tab */}
        <TabsContent value="agents" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <MetricCard
              title="Total Agents"
              value={agents.total_count}
              icon={Bot}
            />
            <MetricCard
              title="Active Agents"
              value={agents.active_agents}
              icon={Activity}
              status="good"
            />
            <MetricCard
              title="Avg Utilization"
              value={agents.avg_utilization_percent}
              unit="%"
              icon={BarChart3}
              status={agents.avg_utilization_percent > 80 ? 'warning' : 'good'}
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Top Agents by Task Count</CardTitle>
              <CardDescription>Most active agents in current window</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {agents.top_agents.map((agent, idx) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{agent.name}</span>
                      <div className="flex items-center gap-4">
                        <span className="text-muted-foreground">
                          {agent.tasks_completed} tasks
                        </span>
                        <span className="font-medium">
                          {agent.utilization_percent?.toFixed(1) || 0}%
                        </span>
                      </div>
                    </div>
                    <Progress value={agent.utilization_percent || 0} />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* LLM Tab */}
        <TabsContent value="llm" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <MetricCard
              title="Total Calls"
              value={llm.total_calls}
              icon={Brain}
            />
            <MetricCard
              title="Total Tokens"
              value={llm.total_tokens.toLocaleString()}
              icon={Database}
            />
            <MetricCard
              title="Total Cost"
              value={`$${llm.total_cost.toFixed(2)}`}
              icon={DollarSign}
            />
            <MetricCard
              title="Avg Latency"
              value={llm.avg_latency}
              unit="s"
              icon={Clock}
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Usage by Model</CardTitle>
              <CardDescription>LLM API calls distribution</CardDescription>
            </CardHeader>
            <CardContent>
              {Object.keys(llm.by_model).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(llm.by_model).map(([model, stats]: [string, any]) => (
                    <div key={model} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium">{model}</span>
                        <span className="text-muted-foreground">
                          {stats.calls} calls • {stats.tokens} tokens
                        </span>
                      </div>
                      <Progress value={(stats.calls / llm.total_calls) * 100} />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-4">No LLM calls yet</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Resources Tab */}
        <TabsContent value="resources" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>CPU Usage</CardTitle>
                <CardDescription>Current CPU utilization</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center justify-between">
                  <Cpu className="w-8 h-8 text-primary" />
                  <span className="text-3xl font-bold">
                    {resources.cpu_percent?.toFixed(1) || 0}%
                  </span>
                </div>
                <Progress value={resources.cpu_percent || 0} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Memory Usage</CardTitle>
                <CardDescription>Current memory utilization</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center justify-between">
                  <Server className="w-8 h-8 text-primary" />
                  <span className="text-3xl font-bold">
                    {resources.memory_percent?.toFixed(1) || 0}%
                  </span>
                </div>
                <Progress value={resources.memory_percent || 0} />
                <p className="text-sm text-muted-foreground">
                  {((resources.memory_bytes || 0) / 1024 / 1024).toFixed(0)} MB used
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tasks Tab */}
        <TabsContent value="tasks" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <MetricCard
              title="Total Tasks"
              value={tasks.total}
              icon={Activity}
            />
            <MetricCard
              title="Successful"
              value={tasks.successful}
              icon={CheckCircle}
              status="good"
            />
            <MetricCard
              title="Failed"
              value={tasks.failed}
              icon={AlertCircle}
              status={tasks.failed > 0 ? 'warning' : 'good'}
            />
            <MetricCard
              title="Success Rate"
              value={(tasks.success_rate * 100).toFixed(1)}
              unit="%"
              icon={TrendingUp}
              status={getSuccessRateStatus(tasks.success_rate * 100)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Token Usage</CardTitle>
                <CardDescription>Total LLM tokens consumed</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {tasks.total_tokens.toLocaleString()}
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  Across {tasks.total} tasks
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Cost Efficiency</CardTitle>
                <CardDescription>Cost per task</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  ${tasks.avg_cost.toFixed(4)}
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  Total: ${tasks.total_cost.toFixed(2)}
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
