/**
 * Governance Console - Phase 1.1 Monitoring Dashboard
 *
 * Real-time monitoring for:
 * - Decision Center decisions
 * - Escalation management
 * - Policy compliance
 * - Audit trail
 */

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  BarChart3,
  Activity,
  Users,
  Settings,
  RefreshCw,
  Bell,
  Eye,
  ThumbsUp,
  ThumbsDown,
  CheckCheck,
  XCircle,
  TrendingUp,
  Zap,
  Database
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { Separator } from './ui/separator';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { ScrollArea } from './ui/scroll-area';
import governanceService, {
  Decision,
  Escalation,
  GovernanceStats,
  PolicySummary
} from '../services/governance';

export function GovernanceConsole() {
  const queryClient = useQueryClient();
  const [selectedTab, setSelectedTab] = useState('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedDecisionId, setSelectedDecisionId] = useState<string | null>(null);

  // ============================================================================
  // Data Fetching
  // ============================================================================

  // Health check
  const { data: health, error: healthError } = useQuery({
    queryKey: ['governance', 'health'],
    queryFn: () => governanceService.getHealth(),
    refetchInterval: autoRefresh ? 5000 : false,
  });

  // Statistics
  const { data: stats } = useQuery({
    queryKey: ['governance', 'stats'],
    queryFn: () => governanceService.getStats(),
    refetchInterval: autoRefresh ? 10000 : false,
  });

  // Recent decisions
  const { data: decisions = [] } = useQuery({
    queryKey: ['governance', 'decisions'],
    queryFn: () => governanceService.getDecisions(50),
    refetchInterval: autoRefresh ? 5000 : false,
  });

  // Active escalations
  const { data: escalations = [] } = useQuery({
    queryKey: ['governance', 'escalations'],
    queryFn: () => governanceService.getEscalations('ACTIVE'),
    refetchInterval: autoRefresh ? 5000 : false,
  });

  // Policy summary
  const { data: policies } = useQuery({
    queryKey: ['governance', 'policies'],
    queryFn: () => governanceService.getPolicySummary(),
    refetchInterval: autoRefresh ? 30000 : false,
  });

  // Audit trail
  const { data: auditTrail = [] } = useQuery({
    queryKey: ['governance', 'audit'],
    queryFn: () => governanceService.getAuditTrail(100),
    refetchInterval: autoRefresh ? 10000 : false,
  });

  // ============================================================================
  // Mutations
  // ============================================================================

  const approveMutation = useMutation({
    mutationFn: (decisionId: string) =>
      governanceService.approveDecision({
        decision_id: decisionId,
        approved_by: 'admin-console',
        notes: 'Approved via admin console'
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['governance'] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (decisionId: string) =>
      governanceService.rejectDecision({
        decision_id: decisionId,
        approved_by: 'admin-console',
        notes: 'Rejected via admin console'
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['governance'] });
    },
  });

  const resolveEscalationMutation = useMutation({
    mutationFn: (escalationId: string) =>
      governanceService.resolveEscalation({
        escalation_id: escalationId,
        resolved_by: 'admin-console',
        resolution_notes: 'Resolved via admin console'
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['governance'] });
    },
  });

  const reloadPoliciesMutation = useMutation({
    mutationFn: () => governanceService.reloadPolicies(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['governance'] });
      alert('✅ Policies reloaded successfully!');
    },
  });

  // ============================================================================
  // Render Helpers
  // ============================================================================

  const getDecisionBadge = (decision: string) => {
    const variants: Record<string, { color: string; icon: any }> = {
      APPROVE: { color: 'bg-green-500', icon: CheckCircle },
      REJECT: { color: 'bg-red-500', icon: XCircle },
      ESCALATE: { color: 'bg-yellow-500', icon: AlertTriangle },
      PENDING: { color: 'bg-blue-500', icon: Clock },
    };
    return variants[decision] || variants.PENDING;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getGovernanceStatus = () => {
    if (healthError) return { color: 'red', label: 'ERROR', icon: AlertTriangle };
    if (!health) return { color: 'gray', label: 'LOADING', icon: RefreshCw };
    if (health.decision_center_active && health.policy_engine_loaded)
      return { color: 'green', label: 'ACTIVE', icon: CheckCircle };
    return { color: 'yellow', label: 'DEGRADED', icon: AlertTriangle };
  };

  const status = getGovernanceStatus();

  // ============================================================================
  // Main Render
  // ============================================================================

  if (healthError) {
    return (
      <div className="p-8">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Governance Layer Unavailable</AlertTitle>
          <AlertDescription>
            Failed to connect to Governance API on port 9091.
            <br />
            Error: {(healthError as Error).message}
            <br />
            <Button
              variant="outline"
              size="sm"
              className="mt-4"
              onClick={() => queryClient.invalidateQueries({ queryKey: ['governance'] })}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry Connection
            </Button>
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
            <Shield className="h-8 w-8 text-blue-600" />
            Governance Console - Phase 1.1
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Decision Center | Policy Engine | Escalation Management
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Auto-refresh toggle */}
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

          {/* Status Badge */}
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
            <CardTitle className="text-sm font-medium">Total Decisions</CardTitle>
            <Activity className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_decisions || 0}</div>
            <Progress value={100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approved</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {stats?.decisions_approved || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {stats?.total_decisions
                ? `${((stats.decisions_approved / stats.total_decisions) * 100).toFixed(1)}%`
                : '0%'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rejected</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {stats?.decisions_rejected || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {stats?.total_decisions
                ? `${((stats.decisions_rejected / stats.total_decisions) * 100).toFixed(1)}%`
                : '0%'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Escalations</CardTitle>
            <Bell className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {stats?.active_escalations || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {stats?.resolved_escalations || 0} resolved
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Maturity Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {stats?.governance_maturity_score || 0}/100
            </div>
            <Progress value={stats?.governance_maturity_score || 0} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Active Escalations Alert */}
      {escalations.length > 0 && (
        <Alert variant="destructive">
          <Bell className="h-4 w-4" />
          <AlertTitle>Active Escalations Require Attention</AlertTitle>
          <AlertDescription>
            {escalations.length} escalation(s) pending resolution. Review the Escalations tab.
          </AlertDescription>
        </Alert>
      )}

      {/* Main Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">
            <BarChart3 className="h-4 w-4 mr-2" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="decisions">
            <CheckCheck className="h-4 w-4 mr-2" />
            Decisions
          </TabsTrigger>
          <TabsTrigger value="escalations">
            <Bell className="h-4 w-4 mr-2" />
            Escalations
          </TabsTrigger>
          <TabsTrigger value="policies">
            <FileText className="h-4 w-4 mr-2" />
            Policies
          </TabsTrigger>
          <TabsTrigger value="audit">
            <Eye className="h-4 w-4 mr-2" />
            Audit
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Governance Health */}
            <Card>
              <CardHeader>
                <CardTitle>Governance Layer Health</CardTitle>
                <CardDescription>Phase 1.1 Components Status</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Decision Center</span>
                  <Badge variant={health?.decision_center_active ? "default" : "destructive"}>
                    {health?.decision_center_active ? 'ACTIVE' : 'INACTIVE'}
                  </Badge>
                </div>
                <Separator />
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Policy Engine</span>
                  <Badge variant={health?.policy_engine_loaded ? "default" : "destructive"}>
                    {health?.policy_engine_loaded ? 'LOADED' : 'NOT LOADED'}
                  </Badge>
                </div>
                <Separator />
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Escalation Manager</span>
                  <Badge variant={health?.escalation_manager_active ? "default" : "destructive"}>
                    {health?.escalation_manager_active ? 'ACTIVE' : 'INACTIVE'}
                  </Badge>
                </div>
                <Separator />
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Total Policies</span>
                  <span className="font-mono font-bold">{health?.total_policies || 0}</span>
                </div>
              </CardContent>
            </Card>

            {/* Policy Compliance */}
            <Card>
              <CardHeader>
                <CardTitle>Policy Compliance</CardTitle>
                <CardDescription>Real-time compliance monitoring</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center py-4">
                  <div className="text-6xl font-bold text-blue-600">
                    {stats?.policy_compliance_rate?.toFixed(1) || '0.0'}%
                  </div>
                  <p className="text-sm text-gray-600 mt-2">Compliance Rate</p>
                </div>
                <Progress value={stats?.policy_compliance_rate || 0} className="h-4" />
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded">
                    <div className="text-2xl font-bold text-green-600">
                      {stats?.decisions_approved || 0}
                    </div>
                    <p className="text-xs text-gray-600">Compliant</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded">
                    <div className="text-2xl font-bold text-red-600">
                      {stats?.decisions_rejected || 0}
                    </div>
                    <p className="text-xs text-gray-600">Non-Compliant</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Performance Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-600" />
                Performance Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Avg Decision Time</p>
                  <p className="text-2xl font-bold">
                    {stats?.avg_decision_time_ms?.toFixed(1) || '0'}ms
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Decisions</p>
                  <p className="text-2xl font-bold">{stats?.total_decisions || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Escalation Rate</p>
                  <p className="text-2xl font-bold">
                    {stats?.total_decisions
                      ? `${((stats.decisions_escalated / stats.total_decisions) * 100).toFixed(1)}%`
                      : '0%'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Decisions Tab */}
        <TabsContent value="decisions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Decisions</CardTitle>
              <CardDescription>Last 50 decisions from Decision Center</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[600px]">
                <div className="space-y-2">
                  {decisions.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">No decisions yet</p>
                  ) : (
                    decisions.map((decision) => {
                      const badge = getDecisionBadge(decision.decision);
                      const Icon = badge.icon;
                      return (
                        <div
                          key={decision.id}
                          className="p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition"
                          onClick={() => setSelectedDecisionId(decision.id)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <Icon className={`h-5 w-5 ${badge.color}`} />
                                <span className="font-medium">{decision.service_name}</span>
                                <Badge variant="outline">{decision.action_type}</Badge>
                              </div>
                              <p className="text-sm text-gray-600 mb-2">{decision.reasoning}</p>
                              <div className="flex items-center gap-4 text-xs text-gray-500">
                                <span>{formatTimestamp(decision.timestamp)}</span>
                                {decision.policy_matched && (
                                  <span className="flex items-center gap-1">
                                    <FileText className="h-3 w-3" />
                                    {decision.policy_matched}
                                  </span>
                                )}
                              </div>
                            </div>
                            {decision.requires_approval && decision.decision === 'PENDING' && (
                              <div className="flex gap-2 ml-4">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    approveMutation.mutate(decision.id);
                                  }}
                                >
                                  <ThumbsUp className="h-4 w-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    rejectMutation.mutate(decision.id);
                                  }}
                                >
                                  <ThumbsDown className="h-4 w-4" />
                                </Button>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Escalations Tab */}
        <TabsContent value="escalations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-yellow-600" />
                Active Escalations
              </CardTitle>
              <CardDescription>Escalations requiring manual intervention</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {escalations.length === 0 ? (
                  <div className="text-center py-8">
                    <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
                    <p className="text-lg font-medium">No Active Escalations</p>
                    <p className="text-sm text-gray-500">All systems operating normally</p>
                  </div>
                ) : (
                  escalations.map((escalation) => (
                    <div key={escalation.id} className="p-4 border border-yellow-500 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="h-5 w-5 text-yellow-600" />
                            <span className="font-medium">{escalation.service_name}</span>
                            <Badge variant="destructive">Level {escalation.level}</Badge>
                          </div>
                          <p className="text-sm mb-2">
                            <span className="font-medium">Trigger:</span> {escalation.trigger}
                          </p>
                          <p className="text-sm mb-2">
                            <span className="font-medium">Action:</span> {escalation.action_type}
                          </p>
                          <div className="flex items-center gap-2 text-xs text-gray-600">
                            <Clock className="h-3 w-3" />
                            {formatTimestamp(escalation.timestamp)}
                          </div>
                        </div>
                        <Button
                          size="sm"
                          onClick={() => resolveEscalationMutation.mutate(escalation.id)}
                        >
                          Resolve
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Policies Tab */}
        <TabsContent value="policies" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-blue-600" />
                  Policy Configuration
                </span>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => reloadPoliciesMutation.mutate()}
                  disabled={reloadPoliciesMutation.isPending}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${reloadPoliciesMutation.isPending ? 'animate-spin' : ''}`} />
                  Reload Policies
                </Button>
              </CardTitle>
              <CardDescription>
                Policy Engine - YAML-based configuration with hot-reload
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-600">Total Policies</p>
                  <p className="text-3xl font-bold">{policies?.total_policies || 0}</p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-600">Critical Services</p>
                  <p className="text-3xl font-bold">{policies?.critical_services || 0}</p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-600">Recovery Policies</p>
                  <p className="text-3xl font-bold">{policies?.recovery_policies || 0}</p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-600">Optimization</p>
                  <p className="text-3xl font-bold">{policies?.optimization_policies || 0}</p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-600">Escalation Rules</p>
                  <p className="text-3xl font-bold">{policies?.escalation_rules || 0}</p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-600">Last Reload</p>
                  <p className="text-sm font-mono mt-2">
                    {policies?.last_reload ? formatTimestamp(policies.last_reload) : 'Never'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Audit Tab */}
        <TabsContent value="audit" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5 text-gray-600" />
                Audit Trail
              </CardTitle>
              <CardDescription>ISO 22301 Compliance - Full decision audit log</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[600px]">
                <div className="space-y-2">
                  {auditTrail.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">No audit entries</p>
                  ) : (
                    auditTrail.map((entry, idx) => (
                      <div key={idx} className="p-3 border rounded text-sm">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">{entry.action}</span>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(entry.timestamp)}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-gray-600">
                          <span>Service: {entry.service}</span>
                          <span>Decision: {entry.decision}</span>
                          {entry.user && <span>User: {entry.user}</span>}
                        </div>
                        <p className="text-xs text-gray-600 mt-1">{entry.reasoning}</p>
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <div className="text-center text-sm text-gray-500 pt-6 border-t">
        <p>
          Governance Console - Phase 1.1 |
          Maturity Score: {stats?.governance_maturity_score || 0}/100 |
          Status: <span className="font-medium text-green-600">
            {health?.decision_center_active ? 'OPERATIONAL' : 'UNAVAILABLE'}
          </span>
        </p>
      </div>
    </div>
  );
}

export default GovernanceConsole;
