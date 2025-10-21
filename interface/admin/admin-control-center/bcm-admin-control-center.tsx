import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
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
  Network,
  Shield,
  Users,
  MessageSquare,
  Zap,
  Eye,
  Code
} from 'lucide-react';

const BCMAdminControlCenter = () => {
  // Mock data - в реальности будет из API
  const [aiOrgans] = useState([
    { id: 1, name: 'Governance Brain', status: 'healthy', load: 45, location: 'ai_orchestrator:8000' },
    { id: 2, name: 'Risk Advisor', status: 'healthy', load: 67, location: 'bia_engine:8082' },
    { id: 3, name: 'Incident Commander', status: 'warning', load: 89, location: 'incident_mgmt:8003' },
    { id: 4, name: 'Training Mentor', status: 'healthy', load: 23, location: 'training_service:8004' },
    { id: 5, name: 'Audit Inspector', status: 'healthy', load: 34, location: 'compliance_checker:8005' },
    { id: 6, name: 'Recovery Planner', status: 'error', load: 0, location: 'recovery_service:8006' },
    { id: 7, name: 'Communication Hub', status: 'healthy', load: 56, location: 'notification_service:8007' },
    { id: 8, name: 'Resource Manager', status: 'healthy', load: 78, location: 'resource_mgmt:8008' },
    { id: 9, name: 'Performance Monitor', status: 'healthy', load: 43, location: 'monitoring:8009' },
    { id: 10, name: 'Knowledge Keeper', status: 'healthy', load: 61, location: 'knowledge_base:8010' }
  ]);

  const [services] = useState([
    { name: 'Odoo BCM Core', port: '8069', status: 'running', uptime: '5d 12h' },
    { name: 'AI Orchestrator', port: '8000', status: 'running', uptime: '5d 12h' },
    { name: 'PostgreSQL', port: '5432', status: 'running', uptime: '7d 3h' },
    { name: 'Redis Cache', port: '6379', status: 'running', uptime: '7d 3h' },
    { name: 'EventBus', port: '8001', status: 'running', uptime: '2d 8h' },
    { name: 'BIA Engine', port: '8082', status: 'running', uptime: '1d 14h' },
    { name: 'Document Processor', port: '8083', status: 'stopped', uptime: '-' },
    { name: 'Grafana', port: '3000', status: 'running', uptime: '7d 3h' },
    { name: 'Prometheus', port: '9090', status: 'running', uptime: '7d 3h' }
  ]);

  const [systemMetrics] = useState({
    cpu: 67,
    memory: 78,
    disk: 45,
    network: 234.5
  });

  const getStatusIcon = (status) => {
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

  const getStatusColor = (status) => {
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

  const handleServiceAction = (service, action) => {
    console.log(`${action} ${service}`);
    // В реальности: API call к Docker/сервисам
  };

  const openPlatform = (url, name) => {
    console.log(`Opening ${name} at ${url}`);
    // В реальности: window.open или iframe
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">BCM Control Center</h1>
            <p className="text-slate-600 mt-2">Digital BCM Organism Management & System Control</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="px-3 py-2">
              <Activity className="h-4 w-4 mr-2" />
              System Online
            </Badge>
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>
      </div>

      <Tabs defaultValue="organisms" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="organisms">AI Organisms</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
          <TabsTrigger value="platforms">Platforms</TabsTrigger>
          <TabsTrigger value="tools">AI Tools</TabsTrigger>
        </TabsList>

        {/* AI Organisms Tab */}
        <TabsContent value="organisms" className="space-y-6">
          <Alert>
            <Brain className="h-4 w-4" />
            <AlertDescription>
              Digital BCM Organism: 10 specialized AI organs working in harmony for intelligent business continuity management
            </AlertDescription>
          </Alert>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {aiOrgans.map((organ) => (
              <Card key={organ.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(organ.status)}
                      <div>
                        <CardTitle className="text-lg">{organ.name}</CardTitle>
                        <CardDescription className="text-sm">{organ.location}</CardDescription>
                      </div>
                    </div>
                    <Badge variant="secondary" className={`${getStatusColor(organ.status)} text-white`}>
                      {organ.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Load</span>
                        <span>{organ.load}%</span>
                      </div>
                      <Progress value={organ.load} className="h-2" />
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        <Settings className="h-4 w-4 mr-1" />
                        Configure
                      </Button>
                      <Button size="sm" variant="outline">
                        <Eye className="h-4 w-4 mr-1" />
                        Monitor
                      </Button>
                      <Button size="sm" variant="outline">
                        <Code className="h-4 w-4 mr-1" />
                        Logs
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Services Tab */}
        <TabsContent value="services" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* System Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  System Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>CPU Usage</span>
                    <span>{systemMetrics.cpu}%</span>
                  </div>
                  <Progress value={systemMetrics.cpu} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Memory</span>
                    <span>{systemMetrics.memory}%</span>
                  </div>
                  <Progress value={systemMetrics.memory} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Disk Usage</span>
                    <span>{systemMetrics.disk}%</span>
                  </div>
                  <Progress value={systemMetrics.disk} className="h-2" />
                </div>
                <div className="pt-2 border-t">
                  <div className="flex justify-between text-sm">
                    <span>Network I/O</span>
                    <span>{systemMetrics.network} MB/s</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Services List */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Server className="h-5 w-5" />
                    Services Management
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {services.map((service, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(service.status)}
                          <div>
                            <div className="font-medium">{service.name}</div>
                            <div className="text-sm text-slate-500">Port: {service.port} • Uptime: {service.uptime}</div>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          {service.status === 'running' ? (
                            <>
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => handleServiceAction(service.name, 'restart')}
                              >
                                <RefreshCw className="h-4 w-4" />
                              </Button>
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => handleServiceAction(service.name, 'stop')}
                              >
                                <Square className="h-4 w-4" />
                              </Button>
                            </>
                          ) : (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => handleServiceAction(service.name, 'start')}
                            >
                              <Play className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Monitoring Tab */}
        <TabsContent value="monitoring" className="space-y-6">
          <div className="grid grid-cols-1 gap-6">
            {/* Grafana Dashboards */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Grafana Dashboards
                </CardTitle>
                <CardDescription>
                  Embedded monitoring dashboards from Grafana + Prometheus
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
                  <Button 
                    variant="outline" 
                    onClick={() => openPlatform('http://localhost:3000/d/bcm-overview', 'BCM Overview')}
                    className="justify-start"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    BCM Overview
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => openPlatform('http://localhost:3000/d/system-resources', 'System Resources')}
                    className="justify-start"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    System Resources
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => openPlatform('http://localhost:3000/d/ai-organisms', 'AI Organisms')}
                    className="justify-start"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    AI Health
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => openPlatform('http://localhost:9090', 'Prometheus')}
                    className="justify-start"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Prometheus
                  </Button>
                </div>
                
                {/* Embedded Grafana Dashboard Preview */}
                <div className="bg-slate-100 rounded-lg p-4 h-96 flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 text-slate-400 mx-auto mb-2" />
                    <p className="text-slate-600">Embedded Grafana Dashboard</p>
                    <p className="text-sm text-slate-500">Live monitoring data will be displayed here</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Prometheus Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">67%</div>
                  <div className="text-xs text-slate-500 mt-1">
                    avg 5min: node_cpu_seconds_total
                  </div>
                  <Progress value={67} className="h-1 mt-2" />
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">4.2GB</div>
                  <div className="text-xs text-slate-500 mt-1">
                    node_memory_MemAvailable_bytes
                  </div>
                  <Progress value={78} className="h-1 mt-2" />
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">HTTP Requests</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">1.2k</div>
                  <div className="text-xs text-slate-500 mt-1">
                    rate(http_requests_total[5m])
                  </div>
                  <div className="text-xs text-green-600 mt-1">↑ 12% from last hour</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Response Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">89ms</div>
                  <div className="text-xs text-slate-500 mt-1">
                    p95 http_request_duration_seconds
                  </div>
                  <div className="text-xs text-green-600 mt-1">↓ 5ms from baseline</div>
                </CardContent>
              </Card>
            </div>

            {/* MCP Integrations Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Network className="h-5 w-5" />
                  MCP Protocol Integrations
                </CardTitle>
                <CardDescription>
                  Model Context Protocol connections and tool integrations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">BCM Tool Server</span>
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    </div>
                    <div className="text-sm text-slate-500">
                      25 BCM tools • Connected
                    </div>
                    <Badge variant="outline" className="mt-2 text-xs">
                      mcp://bcm-platform:8087
                    </Badge>
                  </div>

                  <div className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">File System Tools</span>
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    </div>
                    <div className="text-sm text-slate-500">
                      Document processor • Connected
                    </div>
                    <Badge variant="outline" className="mt-2 text-xs">
                      mcp://filesystem:8088
                    </Badge>
                  </div>

                  <div className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">Database Tools</span>
                      <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    </div>
                    <div className="text-sm text-slate-500">
                      PostgreSQL access • Configuring
                    </div>
                    <Badge variant="outline" className="mt-2 text-xs">
                      mcp://postgres:5432
                    </Badge>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t">
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Configure MCP Servers
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Platforms Tab */}
        <TabsContent value="platforms" className="space-y-6">
          {/* Main Platforms */}
          <Card>
            <CardHeader>
              <CardTitle>BCM Platform Ecosystem</CardTitle>
              <CardDescription>Quick access to all platform components</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Odoo BCM */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('http://localhost:8069', 'Odoo BCM')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Database className="h-5 w-5" />
                      Odoo BCM Core
                    </CardTitle>
                    <CardDescription className="text-sm">25 BCM modules</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">:8069</Badge>
                      <ExternalLink className="h-4 w-4 text-slate-500" />
                    </div>
                  </CardContent>
                </Card>

                {/* User Platform */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('http://localhost:3000', 'User Platform')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Users className="h-5 w-5" />
                      User Platform
                    </CardTitle>
                    <CardDescription className="text-sm">React interface</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">:3000</Badge>
                      <ExternalLink className="h-4 w-4 text-slate-500" />
                    </div>
                  </CardContent>
                </Card>

                {/* AI Orchestrator */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('http://localhost:8000', 'AI Orchestrator')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Brain className="h-5 w-5" />
                      AI Orchestrator
                    </CardTitle>
                    <CardDescription className="text-sm">AI coordination</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">:8000</Badge>
                      <ExternalLink className="h-4 w-4 text-slate-500" />
                    </div>
                  </CardContent>
                </Card>

                {/* Community Portal */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('http://localhost:8084', 'Community')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <MessageSquare className="h-5 w-5" />
                      Community Portal
                    </CardTitle>
                    <CardDescription className="text-sm">Knowledge sharing</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">:8084</Badge>
                      <ExternalLink className="h-4 w-4 text-slate-500" />
                    </div>
                  </CardContent>
                </Card>

                {/* Digital Twin */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('http://localhost:8085', 'Digital Twin')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Zap className="h-5 w-5" />
                      Digital Twin
                    </CardTitle>
                    <CardDescription className="text-sm">3D simulation</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">:8085</Badge>
                      <ExternalLink className="h-4 w-4 text-slate-500" />
                    </div>
                  </CardContent>
                </Card>

                {/* Security Admin */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('http://localhost:8080', 'Keycloak')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Shield className="h-5 w-5" />
                      Keycloak SSO
                    </CardTitle>
                    <CardDescription className="text-sm">User management</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">:8080</Badge>
                      <ExternalLink className="h-4 w-4 text-slate-500" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>

          {/* External Services & Infrastructure */}
          <Card>
            <CardHeader>
              <CardTitle>External Services & Infrastructure</CardTitle>
              <CardDescription>Quick access to cloud services, repositories, and databases</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Docker Hub */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('https://hub.docker.com/r/sehfoundation/bcm-platform', 'Docker Hub')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <Server className="h-4 w-4" />
                      Docker Hub
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs text-slate-500">Container registry</div>
                    <ExternalLink className="h-3 w-3 text-slate-400 mt-2" />
                  </CardContent>
                </Card>

                {/* GitHub */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('https://github.com/SEH-Foundation/ISO-22301', 'GitHub')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <Code className="h-4 w-4" />
                      GitHub Repo
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs text-slate-500">Source code</div>
                    <ExternalLink className="h-3 w-3 text-slate-400 mt-2" />
                  </CardContent>
                </Card>

                {/* Supabase */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('https://supabase.com/dashboard/project/mvzlkpzakzlmmxyjjtvr', 'Supabase')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <Database className="h-4 w-4" />
                      Supabase DB
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs text-slate-500">AI Memory & Analytics</div>
                    <ExternalLink className="h-3 w-3 text-slate-400 mt-2" />
                  </CardContent>
                </Card>

                {/* PostgreSQL Admin */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('http://localhost:5050', 'pgAdmin')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <Database className="h-4 w-4" />
                      pgAdmin
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs text-slate-500">Database admin</div>
                    <Badge variant="outline" className="text-xs mt-1">:5050</Badge>
                  </CardContent>
                </Card>

                {/* Redis Admin */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('http://localhost:8081', 'Redis Commander')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <Activity className="h-4 w-4" />
                      Redis Admin
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs text-slate-500">Cache management</div>
                    <Badge variant="outline" className="text-xs mt-1">:8081</Badge>
                  </CardContent>
                </Card>

                {/* Anthropic Console */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('https://console.anthropic.com', 'Anthropic')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <Brain className="h-4 w-4" />
                      Anthropic
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs text-slate-500">AI API console</div>
                    <ExternalLink className="h-3 w-3 text-slate-400 mt-2" />
                  </CardContent>
                </Card>

                {/* Railway */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('https://railway.app', 'Railway')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <Zap className="h-4 w-4" />
                      Railway
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs text-slate-500">Deployment platform</div>
                    <ExternalLink className="h-3 w-3 text-slate-400 mt-2" />
                  </CardContent>
                </Card>

                {/* Vercel */}
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                      onClick={() => openPlatform('https://vercel.com/dashboard', 'Vercel')}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <ExternalLink className="h-4 w-4" />
                      Vercel
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs text-slate-500">Frontend hosting</div>
                    <ExternalLink className="h-3 w-3 text-slate-400 mt-2" />
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>

          {/* Development Tools */}
          <Card>
            <CardHeader>
              <CardTitle>Development & Monitoring Tools</CardTitle>
              <CardDescription>Local development and monitoring tools</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                <Button variant="outline" onClick={() => openPlatform('http://localhost:3000', 'Grafana')} className="justify-start h-auto p-3">
                  <div className="flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" />
                    <div className="text-left">
                      <div className="font-medium">Grafana</div>
                      <div className="text-xs text-slate-500">:3000</div>
                    </div>
                  </div>
                </Button>

                <Button variant="outline" onClick={() => openPlatform('http://localhost:9090', 'Prometheus')} className="justify-start h-auto p-3">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4" />
                    <div className="text-left">
                      <div className="font-medium">Prometheus</div>
                      <div className="text-xs text-slate-500">:9090</div>
                    </div>
                  </div>
                </Button>

                <Button variant="outline" onClick={() => openPlatform('http://localhost:9093', 'AlertManager')} className="justify-start h-auto p-3">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    <div className="text-left">
                      <div className="font-medium">AlertManager</div>
                      <div className="text-xs text-slate-500">:9093</div>
                    </div>
                  </div>
                </Button>

                <Button variant="outline" onClick={() => openPlatform('http://localhost:3100', 'Loki Logs')} className="justify-start h-auto p-3">
                  <div className="flex items-center gap-2">
                    <Eye className="h-4 w-4" />
                    <div className="text-left">
                      <div className="font-medium">Loki Logs</div>
                      <div className="text-xs text-slate-500">:3100</div>
                    </div>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Tools Tab */}
        <TabsContent value="tools" className="space-y-6">
          <Alert>
            <Code className="h-4 w-4" />
            <AlertDescription>
              Ready-made Anthropic tools for AI development and testing
            </AlertDescription>
          </Alert>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* MCP Inspector */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="h-5 w-5" />
                  MCP Inspector
                </CardTitle>
                <CardDescription>
                  Visual testing tool for Model Context Protocol servers
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm text-slate-600">
                  Ready-made tool for testing and debugging AI organs communication
                </div>
                <Button className="w-full" onClick={() => openPlatform('#mcp-inspector', 'MCP Inspector')}>
                  <Eye className="h-4 w-4 mr-2" />
                  Open MCP Inspector
                </Button>
              </CardContent>
            </Card>

            {/* Prompt Studio */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="h-5 w-5" />
                  Prompt Engineering Studio
                </CardTitle>
                <CardDescription>
                  Interactive playground for prompt optimization
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm text-slate-600">
                  Test and optimize prompts for each AI organ with real-time feedback
                </div>
                <Button className="w-full" onClick={() => openPlatform('#prompt-studio', 'Prompt Studio')}>
                  <Code className="h-4 w-4 mr-2" />
                  Open Prompt Studio
                </Button>
              </CardContent>
            </Card>

            {/* Token Monitor */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Token Usage Monitor
                </CardTitle>
                <CardDescription>
                  Track Anthropic API usage and costs
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm text-slate-600">
                  Monitor token consumption across all AI organs
                </div>
                <Button className="w-full" onClick={() => openPlatform('#token-monitor', 'Token Monitor')}>
                  <BarChart3 className="h-4 w-4 mr-2" />
                  View Usage Analytics
                </Button>
              </CardContent>
            </Card>

            {/* AI Organism Evolution */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  Organism Evolution
                </CardTitle>
                <CardDescription>
                  Track learning and adaptation of AI organs
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm text-slate-600">
                  Monitor how AI organs learn and improve over time
                </div>
                <Button className="w-full" onClick={() => openPlatform('#evolution', 'Evolution Tracker')}>
                  <Brain className="h-4 w-4 mr-2" />
                  View Evolution Metrics
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BCMAdminControlCenter;