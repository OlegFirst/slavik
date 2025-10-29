import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  Activity,
  Server,
  Database,
  Network,
  Cpu,
  HardDrive,
  MemoryStick,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Info,
  Clock,
  TrendingUp,
  TrendingDown,
  Wifi,
  WifiOff,
  Zap,
  Eye,
  Settings
} from 'lucide-react';

interface SystemHealth {
  status: 'healthy' | 'warning' | 'critical';
  uptime: string;
  last_check: string;
  services: {
    odoo: { status: 'online' | 'offline' | 'degraded', response_time: number };
    document_processor: { status: 'online' | 'offline' | 'degraded', response_time: number };
    ai_control: { status: 'online' | 'offline' | 'degraded', response_time: number };
    database: { status: 'online' | 'offline' | 'degraded', connections: number };
  };
  resources: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    network_io: { in: number; out: number };
  };
  metrics: {
    total_requests: number;
    avg_response_time: number;
    error_rate: number;
    active_users: number;
  };
}

interface Alert {
  id: string;
  type: 'info' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  resolved: boolean;
}

const SystemMonitor: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadSystemHealth();
    loadSystemAlerts();

    if (autoRefresh) {
      const interval = setInterval(() => {
        loadSystemHealth();
        loadSystemAlerts();
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadSystemHealth = async () => {
    setLoading(true);
    try {
      console.log('📊 Loading system health metrics...');

      // Simulate system health check - in real implementation, this would call backend APIs
      const healthData: SystemHealth = {
        status: 'healthy',
        uptime: '15 days, 8 hours',
        last_check: new Date().toISOString(),
        services: {
          odoo: { status: 'online', response_time: 245 },
          document_processor: { status: 'online', response_time: 156 },
          ai_control: { status: 'degraded', response_time: 890 },
          database: { status: 'online', connections: 45 }
        },
        resources: {
          cpu_usage: 35,
          memory_usage: 68,
          disk_usage: 42,
          network_io: { in: 1.2, out: 0.8 }
        },
        metrics: {
          total_requests: 145632,
          avg_response_time: 298,
          error_rate: 0.8,
          active_users: 127
        }
      };

      setHealth(healthData);
      console.log('✅ System health loaded');
    } catch (error) {
      console.error('❌ Failed to load system health:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSystemAlerts = async () => {
    try {
      // Simulate alerts - in real implementation, this would call monitoring APIs
      const alertsData: Alert[] = [
        {
          id: '1',
          type: 'warning',
          title: 'High Memory Usage',
          message: 'Memory usage is at 68% and approaching threshold',
          timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
          resolved: false
        },
        {
          id: '2',
          type: 'warning',
          title: 'AI Control Service Slow',
          message: 'AI Control Center response time is 890ms, above 500ms threshold',
          timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
          resolved: false
        },
        {
          id: '3',
          type: 'info',
          title: 'Scheduled Backup Completed',
          message: 'Daily system backup completed successfully',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          resolved: true
        }
      ];

      setAlerts(alertsData);
    } catch (error) {
      console.error('❌ Failed to load alerts:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'degraded':
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'offline':
      case 'critical':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Info className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'degraded':
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'offline':
      case 'critical':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getResourceColor = (usage: number) => {
    if (usage < 50) return 'bg-green-500';
    if (usage < 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-lg">Loading system monitoring data...</span>
      </div>
    );
  }

  if (!health) {
    return (
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Monitoring Unavailable</AlertTitle>
        <AlertDescription>
          Unable to load system monitoring data. Please check the monitoring service configuration.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* System Status Overview */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            {getStatusIcon(health.status)}
            <span className="text-lg font-semibold">System Status</span>
            <Badge className={getStatusColor(health.status)}>
              {health.status.toUpperCase()}
            </Badge>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>Uptime: {health.uptime}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {autoRefresh ? (
              <>
                <Zap className="h-4 w-4 mr-2" />
                Auto-refresh ON
              </>
            ) : (
              <>
                <Settings className="h-4 w-4 mr-2" />
                Auto-refresh OFF
              </>
            )}
          </Button>
          <Button variant="outline" size="sm" onClick={loadSystemHealth}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Total Requests</p>
                <p className="text-2xl font-bold">{health.metrics.total_requests.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Avg Response</p>
                <p className="text-2xl font-bold">{health.metrics.avg_response_time}ms</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Error Rate</p>
                <p className="text-2xl font-bold">{health.metrics.error_rate}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Eye className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Active Users</p>
                <p className="text-2xl font-bold">{health.metrics.active_users}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Monitoring Tabs */}
      <Tabs defaultValue="services" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="logs">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="services">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Odoo ERP
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(health.services.odoo.status)}
                    <Badge className={getStatusColor(health.services.odoo.status)}>
                      {health.services.odoo.status}
                    </Badge>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {health.services.odoo.response_time}ms
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Server className="h-5 w-5" />
                  Document Processor
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(health.services.document_processor.status)}
                    <Badge className={getStatusColor(health.services.document_processor.status)}>
                      {health.services.document_processor.status}
                    </Badge>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {health.services.document_processor.response_time}ms
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  AI Control Center
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(health.services.ai_control.status)}
                    <Badge className={getStatusColor(health.services.ai_control.status)}>
                      {health.services.ai_control.status}
                    </Badge>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {health.services.ai_control.response_time}ms
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Database
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(health.services.database.status)}
                    <Badge className={getStatusColor(health.services.database.status)}>
                      {health.services.database.status}
                    </Badge>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {health.services.database.connections} connections
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="resources">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cpu className="h-5 w-5" />
                  CPU Usage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Current</span>
                    <span>{health.resources.cpu_usage}%</span>
                  </div>
                  <Progress
                    value={health.resources.cpu_usage}
                    className="h-2"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MemoryStick className="h-5 w-5" />
                  Memory Usage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Current</span>
                    <span>{health.resources.memory_usage}%</span>
                  </div>
                  <Progress
                    value={health.resources.memory_usage}
                    className="h-2"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HardDrive className="h-5 w-5" />
                  Disk Usage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Current</span>
                    <span>{health.resources.disk_usage}%</span>
                  </div>
                  <Progress
                    value={health.resources.disk_usage}
                    className="h-2"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Network className="h-5 w-5" />
                  Network I/O
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Incoming</span>
                    <span className="text-sm font-mono">{health.resources.network_io.in} MB/s</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Outgoing</span>
                    <span className="text-sm font-mono">{health.resources.network_io.out} MB/s</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="alerts">
          <div className="space-y-4">
            {alerts.map(alert => (
              <Alert key={alert.id} className={
                alert.type === 'error' ? 'border-red-200' :
                alert.type === 'warning' ? 'border-yellow-200' :
                'border-blue-200'
              }>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    {alert.type === 'error' ? <XCircle className="h-4 w-4 text-red-600 mt-0.5" /> :
                     alert.type === 'warning' ? <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5" /> :
                     <Info className="h-4 w-4 text-blue-600 mt-0.5" />}
                    <div>
                      <AlertTitle className="flex items-center gap-2">
                        {alert.title}
                        {alert.resolved && <Badge variant="outline" className="text-xs">Resolved</Badge>}
                      </AlertTitle>
                      <AlertDescription className="mt-1">
                        {alert.message}
                      </AlertDescription>
                      <p className="text-xs text-muted-foreground mt-2">
                        {new Date(alert.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              </Alert>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="logs">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>System activity and events from the last 24 hours</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>System health check completed</span>
                  <span className="text-muted-foreground">2 minutes ago</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <RefreshCw className="h-4 w-4 text-blue-600" />
                  <span>Template service restarted</span>
                  <span className="text-muted-foreground">15 minutes ago</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  <span>High memory usage detected</span>
                  <span className="text-muted-foreground">25 minutes ago</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Monitoring Status */}
      <Alert>
        <Activity className="h-4 w-4" />
        <AlertTitle>System Monitoring Active</AlertTitle>
        <AlertDescription>
          Real-time monitoring of Odoo, Document Processor, AI Control Center and system resources.
          Auto-refresh is {autoRefresh ? 'enabled' : 'disabled'} - updates every 30 seconds.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default SystemMonitor;