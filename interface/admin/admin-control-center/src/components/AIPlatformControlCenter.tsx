import React, { useState } from 'react';
import { useSystemData } from '@/hooks/useSystemData';
import { useAppStore } from '@/stores/system';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Activity,
  Brain,
  Server,
  Settings,
  ExternalLink,
  Play,
  Square,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  Database,
  Shield,
  Users,
  Wifi,
  WifiOff,
  Wrench,
  Eye,
  FileText,
  Workflow,
  X
} from 'lucide-react';

// Import all components from original BCM Control Center
import { AIOrganModals } from '@/components/modals/AIOrganModals';
import ModulesOverview from '@/pages/ModulesOverview';
import ComplianceDashboard from '@/components/ComplianceDashboard';
import { Analytics } from '@/pages/Analytics';
import SystemConfigManager from '@/components/SystemConfigManager';
import TemplateManager from '@/components/TemplateManager';
import ClientManager from '@/components/ClientManager';
import SystemMonitor from '@/components/SystemMonitor';
import UserManager from '@/components/UserManager';
import CentralizedArchitectureMonitor from '@/components/CentralizedArchitectureMonitor';

// Import NEW components (Prometheus, Grafana, Tools, Orchestrator)
import ToolsManager from '@/components/ToolsManager';
import GrafanaViewer from '@/components/GrafanaViewer';
import PrometheusMetrics from '@/components/PrometheusMetrics';
import PlatformDashboard from '@/components/PlatformDashboard';
import OrchestratorDashboard from '@/components/OrchestratorDashboard';
import MonitoringDashboard from '@/pages/MonitoringDashboard';

import analyticsHubService, { AIInsight, KPIMetric, UnifiedMetrics } from '@/services/analytics-hub';
import type { AIOrgan } from '@/services/bcm';

// Compliance data
const COMPLETE_MODULE_COMPLIANCE_MATRIX = {
  'AI Foundation': { current_compliance: 90 },
  'Workflow Intelligence': { current_compliance: 85 },
  'Community Intelligence': { current_compliance: 80 },
  'Predictive Service': { current_compliance: 75 },
  'Analytics Specialist': { current_compliance: 88 },
  'Orchestration': { current_compliance: 92 }
};

const AIPlatformControlCenter: React.FC = () => {
  const { aiOrgans, systemMetrics, services, loading, refreshAll, controlService, isRefreshing, fetchServices } = useSystemData();
  const { autoRefresh, setAutoRefresh, refreshInterval, setRefreshInterval, notifications } = useAppStore();

  // Modal state for AI organs
  const [selectedOrgan, setSelectedOrgan] = useState<AIOrgan | null>(null);
  const [modalType, setModalType] = useState<'configure' | 'monitor' | 'logs' | null>(null);
  const [activeDashboard, setActiveDashboard] = useState<'grafana' | 'prometheus' | 'system' | 'realtime'>('grafana');

  // Platform management state
  const [platforms, setPlatforms] = useState([
    { id: 1, name: 'AI Orchestrator', url: 'http://localhost:8000', icon: 'Brain', description: 'AI coordination system' },
    { id: 2, name: 'Workflow Intelligence', url: 'http://localhost:8003', icon: 'Workflow', description: 'Workflow engine' },
    { id: 3, name: 'Community Intelligence', url: 'http://localhost:8004', icon: 'Users', description: 'Community system' },
    { id: 4, name: 'Analytics Specialist', url: 'http://localhost:8051', icon: 'BarChart3', description: 'Analytics & Tools' },
    { id: 5, name: 'Grafana', url: 'http://localhost:3000', icon: 'BarChart3', description: 'Monitoring dashboard' },
    { id: 6, name: 'Prometheus', url: 'http://localhost:9090', icon: 'Activity', description: 'Metrics collection' },
    { id: 7, name: 'Supabase', url: 'https://supabase.com/dashboard', icon: 'Database', description: 'Cloud database' }
  ]);

  const [showAddPlatform, setShowAddPlatform] = useState(false);
  const [newPlatform, setNewPlatform] = useState({ name: '', url: '', description: '', icon: 'ExternalLink' });

  // Analytics state
  const [analyticsData, setAnalyticsData] = useState({
    visits: { today: 0, week: 0, month: 0, trend: 'N/A' },
    popularPages: [],
    topQueries: [],
    userActivity: {
      activeUsers: 0,
      avgSessionTime: 'N/A',
      bounceRate: 'N/A',
      newUsers: 0,
      returningUsers: 0
    }
  });

  const [analyticsConnected, setAnalyticsConnected] = useState(false);

  // Intelligence Hub data
  const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
  const [kpiMetrics, setKpiMetrics] = useState<KPIMetric[]>([]);
  const [unifiedMetrics, setUnifiedMetrics] = useState<UnifiedMetrics | null>(null);
  const [intelligenceHubReady, setIntelligenceHubReady] = useState(false);

  const [selectedTimeRange, setSelectedTimeRange] = useState('week');

  const openOrganModal = (organ: AIOrgan, type: 'configure' | 'monitor' | 'logs') => {
    setSelectedOrgan(organ);
    setModalType(type);
  };

  const closeOrganModal = () => {
    setSelectedOrgan(null);
    setModalType(null);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'running':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'error':
      case 'stopped':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'running':
        return 'bg-green-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'error':
      case 'stopped':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const openPlatform = (url: string, name: string) => {
    if (url.startsWith('#')) {
      alert(` ${name} feature is coming soon!`);
      return;
    }
    if (url.startsWith('/')) {
      window.location.href = url;
      return;
    }
    window.open(url, '_blank');
  };

  const addPlatform = () => {
    if (!newPlatform.name || !newPlatform.url) {
      alert('Please fill in name and URL');
      return;
    }
    const platform = { id: Date.now(), ...newPlatform };
    setPlatforms(prev => [...prev, platform]);
    setNewPlatform({ name: '', url: '', description: '', icon: 'ExternalLink' });
    setShowAddPlatform(false);
    localStorage.setItem('ai-platform-custom-platforms', JSON.stringify([...platforms, platform]));
  };

  const removePlatform = (id: number) => {
    if (confirm('Are you sure you want to remove this platform?')) {
      const updated = platforms.filter(p => p.id !== id);
      setPlatforms(updated);
      localStorage.setItem('ai-platform-custom-platforms', JSON.stringify(updated));
    }
  };

  const getIcon = (iconName: string) => {
    const icons = { Database, Brain, BarChart3, Activity, ExternalLink, Server, Shield, Users, Workflow };
    const IconComponent = icons[iconName as keyof typeof icons] || ExternalLink;
    return <IconComponent className="h-6 w-6 mb-2" />;
  };

  const refreshAnalytics = async () => {
    console.log(' Attempting to fetch real analytics data...');
    try {
      const [insights, metrics, unified] = await Promise.all([
        analyticsHubService.getAIInsights(),
        analyticsHubService.getKPIMetrics(),
        analyticsHubService.getUnifiedMetrics()
      ]);
      setAiInsights(insights);
      setKpiMetrics(metrics);
      setUnifiedMetrics(unified);
      setIntelligenceHubReady(true);

      const { analyticsService } = await import('@/services/bcm');
      const realData = await analyticsService.getRealAnalyticsData();
      if (realData.connected) {
        const enhancedData = await analyticsHubService.enhanceExistingAnalytics(realData);
        setAnalyticsData(enhancedData);
        setAnalyticsConnected(true);
        console.log(' Analytics connected with Intelligence Hub integration');
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      setAnalyticsConnected(false);
    }
  };

  const getHealthySummary = () => {
    const healthyOrgans = aiOrgans.filter(organ => organ.status === 'healthy').length;
    const runningServices = services.filter(service => service.status === 'running').length;
    return {
      organs: { healthy: healthyOrgans, total: aiOrgans.length },
      services: { running: runningServices, total: services.length }
    };
  };

  const handleServiceControl = async (serviceName: string, action: 'start' | 'stop' | 'restart') => {
    const confirmAction = confirm(`Are you sure you want to ${action} ${serviceName}?`);
    if (!confirmAction) return;

    try {
      await controlService(serviceName, action);
      setTimeout(() => {
        fetchServices();
      }, 2000);
    } catch (error: any) {
      console.error('Service control failed:', error);
    }
  };

  const healthSummary = getHealthySummary();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">AI Platform ISO Control Center</h1>
            <p className="text-slate-600 mt-2">Intelligent System Management & Monitoring</p>
            <div className="flex items-center gap-4 mt-3">
              <Badge variant="outline" className="px-3 py-1">
                <Brain className="h-4 w-4 mr-2" />
                {healthSummary.organs.healthy}/{healthSummary.organs.total} AI Services Healthy
              </Badge>
              <Badge variant="outline" className="px-3 py-1">
                <Server className="h-4 w-4 mr-2" />
                {healthSummary.services.running}/{healthSummary.services.total} Services Running
              </Badge>
              <Badge variant="outline" className="px-3 py-1">
                <Shield className="h-4 w-4 mr-2" />
                ISO 22301: {Math.round(Object.values(COMPLETE_MODULE_COMPLIANCE_MATRIX).reduce((sum, m) => sum + m.current_compliance, 0) / Object.keys(COMPLETE_MODULE_COMPLIANCE_MATRIX).length)}% Compliance
              </Badge>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {/* Auto-refresh toggle */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={autoRefresh ? 'bg-green-50 border-green-200' : ''}
              >
                {autoRefresh ? <Wifi className="h-4 w-4 mr-2" /> : <WifiOff className="h-4 w-4 mr-2" />}
                Auto-Refresh
              </Button>
              {autoRefresh && (
                <select
                  value={refreshInterval}
                  onChange={(e) => setRefreshInterval(Number(e.target.value))}
                  className="px-2 py-1 text-sm border rounded"
                >
                  <option value={10000}>10s</option>
                  <option value={30000}>30s</option>
                  <option value={60000}>1m</option>
                  <option value={300000}>5m</option>
                </select>
              )}
            </div>

            <Badge variant="outline" className="px-3 py-2">
              <Activity className="h-4 w-4 mr-2" />
              {isRefreshing ? 'Updating...' : 'System Online'}
            </Badge>
            <Button variant="outline" size="sm" onClick={refreshAll} disabled={isRefreshing}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh Now
            </Button>
          </div>
        </div>

        {/* Notifications */}
        {notifications.length > 0 && (
          <div className="mt-4 space-y-2">
            {notifications.slice(-3).map((notification) => (
              <Alert key={notification.id} className={`relative ${
                notification.type === 'error' ? 'border-red-200 bg-red-50' :
                notification.type === 'warning' ? 'border-yellow-200 bg-yellow-50' :
                'border-green-200 bg-green-50'
              }`}>
                {notification.type === 'error' && <XCircle className="h-4 w-4" />}
                {notification.type === 'warning' && <AlertTriangle className="h-4 w-4" />}
                {notification.type === 'success' && <CheckCircle className="h-4 w-4" />}
                <AlertDescription>
                  <strong>{notification.title}:</strong> {notification.message}
                </AlertDescription>
              </Alert>
            ))}
          </div>
        )}
      </div>

      <Tabs defaultValue="dashboard" className="space-y-6">
        <TabsList className="grid w-full grid-cols-8">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="orchestrator">Orchestrator</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="tools">Tools</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
          <TabsTrigger value="platforms">Platforms</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="compliance">ISO 22301</TabsTrigger>
          <TabsTrigger value="config">System Config</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="clients">Clients</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="modules">Modules</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab - NEW: Combined overview */}
        <TabsContent value="dashboard" className="space-y-6">
          <PlatformDashboard />
        </TabsContent>

        {/* Orchestrator Performance Tab - NEW: Real-time orchestrator monitoring */}
        <TabsContent value="orchestrator" className="space-y-6">
          <Alert>
            <Activity className="h-4 w-4" />
            <AlertDescription>
              Real-time AI Orchestrator Performance Monitoring: Golden metrics, agent utilization, LLM performance, and cost tracking
            </AlertDescription>
          </Alert>
          <OrchestratorDashboard />
        </TabsContent>

        {/* Services Tab - From BCM Control Center */}
        <TabsContent value="services" className="space-y-6">
          <CentralizedArchitectureMonitor />
        </TabsContent>

        {/* Tools Tab - NEW: Analytics Specialist Tools Integration */}
        <TabsContent value="tools" className="space-y-6">
          <Alert>
            <Wrench className="h-4 w-4" />
            <AlertDescription>
              AI Platform Tools: Browse, execute, and manage automated analysis tools via Analytics Specialist API
            </AlertDescription>
          </Alert>
          <ToolsManager />
        </TabsContent>

        {/* Monitoring Tab - NEW: Prometheus + Grafana */}
        <TabsContent value="monitoring" className="space-y-6">
          <div className="flex gap-2 mb-4">
            <Button
              variant={activeDashboard === 'realtime' ? 'default' : 'outline'}
              onClick={() => setActiveDashboard('realtime')}
            >
              <Activity className="h-4 w-4 mr-2" />
              Realtime Dashboard
            </Button>
            <Button
              variant={activeDashboard === 'grafana' ? 'default' : 'outline'}
              onClick={() => setActiveDashboard('grafana')}
            >
              <Eye className="h-4 w-4 mr-2" />
              Grafana Dashboards
            </Button>
            <Button
              variant={activeDashboard === 'prometheus' ? 'default' : 'outline'}
              onClick={() => setActiveDashboard('prometheus')}
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              Prometheus Metrics
            </Button>
            <Button
              variant={activeDashboard === 'system' ? 'default' : 'outline'}
              onClick={() => setActiveDashboard('system')}
            >
              <Server className="h-4 w-4 mr-2" />
              System Monitor
            </Button>
          </div>

          {activeDashboard === 'realtime' && <MonitoringDashboard />}
          {activeDashboard === 'grafana' && <GrafanaViewer />}
          {activeDashboard === 'prometheus' && <PrometheusMetrics />}
          {activeDashboard === 'system' && <SystemMonitor />}
        </TabsContent>

        {/* Platforms Tab - From BCM Control Center */}
        <TabsContent value="platforms" className="space-y-6">
          <Alert>
            <ExternalLink className="h-4 w-4" />
            <AlertDescription>
              Quick access to all integrated platforms and services
            </AlertDescription>
          </Alert>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {platforms.map((platform) => (
              <Card key={platform.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      {getIcon(platform.icon)}
                      <CardTitle className="text-lg">{platform.name}</CardTitle>
                      <CardDescription className="text-sm mt-1">{platform.description}</CardDescription>
                    </div>
                    {platform.id > 7 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          removePlatform(platform.id);
                        }}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => openPlatform(platform.url, platform.name)}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Open
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {showAddPlatform && (
            <Card>
              <CardHeader>
                <CardTitle>Add New Platform</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <input
                  type="text"
                  placeholder="Platform Name"
                  className="w-full px-3 py-2 border rounded"
                  value={newPlatform.name}
                  onChange={(e) => setNewPlatform({ ...newPlatform, name: e.target.value })}
                />
                <input
                  type="text"
                  placeholder="URL"
                  className="w-full px-3 py-2 border rounded"
                  value={newPlatform.url}
                  onChange={(e) => setNewPlatform({ ...newPlatform, url: e.target.value })}
                />
                <input
                  type="text"
                  placeholder="Description"
                  className="w-full px-3 py-2 border rounded"
                  value={newPlatform.description}
                  onChange={(e) => setNewPlatform({ ...newPlatform, description: e.target.value })}
                />
                <div className="flex gap-2">
                  <Button onClick={addPlatform}>Add Platform</Button>
                  <Button variant="outline" onClick={() => setShowAddPlatform(false)}>Cancel</Button>
                </div>
              </CardContent>
            </Card>
          )}

          {!showAddPlatform && (
            <Button onClick={() => setShowAddPlatform(true)}>
              + Add New Platform
            </Button>
          )}
        </TabsContent>

        {/* Analytics Tab - From BCM Control Center */}
        <TabsContent value="analytics" className="space-y-6">
          <Analytics />
        </TabsContent>

        {/* ISO 22301 Compliance Tab */}
        <TabsContent value="compliance" className="space-y-6">
          <ComplianceDashboard />
        </TabsContent>

        {/* System Config Tab */}
        <TabsContent value="config" className="space-y-6">
          <SystemConfigManager />
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-6">
          <TemplateManager />
        </TabsContent>

        {/* Clients Tab */}
        <TabsContent value="clients" className="space-y-6">
          <ClientManager />
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-6">
          <UserManager />
        </TabsContent>

        {/* Modules Tab */}
        <TabsContent value="modules" className="space-y-6">
          <ModulesOverview />
        </TabsContent>
      </Tabs>

      {/* AI Organ Modals */}
      {selectedOrgan && modalType && (
        <AIOrganModals
          organ={selectedOrgan}
          type={modalType}
          onClose={closeOrganModal}
        />
      )}
    </div>
  );
};

export default AIPlatformControlCenter;
