import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Activity,
  Heart,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Server,
  Database,
  Network,
  Cpu,
  HardDrive,
  MemoryStick,
  Wifi,
  WifiOff,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  Zap,
  Shield,
  Eye,
  Settings,
  BarChart3,
  Users,
  Package,
  Brain,
  Gauge
} from 'lucide-react';
import { digitalTwinAPI, SystemHealth, ServiceHealth, PerformanceMetrics, HealthAlert } from '@/services/digitalTwinAPI';
import { useSystemHealth, useRealTimeMetrics } from '@/contexts/DigitalTwinContext';

interface SystemHealthMonitorProps {
  className?: string;
}

interface HealthDimension {
  name: string;
  score: number;
  status: 'healthy' | 'warning' | 'error';
  trend: number;
  description: string;
  icon: React.ReactNode;
}

const SystemHealthMonitor: React.FC<SystemHealthMonitorProps> = ({ className }) => {
  const { systemHealth, connected } = useSystemHealth();
  const [serviceHealth, setServiceHealth] = useState<ServiceHealth[]>([]);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [healthAlerts, setHealthAlerts] = useState<HealthAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('1h');
  const [liveHealthMetrics, setLiveHealthMetrics] = useState<any[]>([]);
  const [criticalAlerts, setCriticalAlerts] = useState<HealthAlert[]>([]);

  // Real-time health metrics
  useRealTimeMetrics('system_health_update', (data) => {
    setLiveHealthMetrics(prev => [
      { ...data, timestamp: new Date(), id: Date.now() },
      ...prev.slice(0, 99) // Keep last 100 metrics
    ]);
    setLastUpdate(new Date());
  });

  // Real-time service health updates
  useRealTimeMetrics('service_health_update', (data) => {
    setServiceHealth(prev => {
      const updated = [...prev];
      const index = updated.findIndex(s => s.name === data.serviceName);
      if (index >= 0) {
        updated[index] = { ...updated[index], ...data };
      }
      return updated;
    });
  });

  // Real-time performance metrics
  useRealTimeMetrics('performance_metrics', (data) => {
    setPerformanceMetrics(data);
    setLastUpdate(new Date());
  });

  // Real-time health alerts
  useRealTimeMetrics('health_alert', (data) => {
    const newAlert = { ...data, timestamp: new Date().toISOString() };

    setHealthAlerts(prev => [newAlert, ...prev.slice(0, 19)]); // Keep last 20 alerts

    // Add to critical alerts if severity is error
    if (data.severity === 'error') {
      setCriticalAlerts(prev => [newAlert, ...prev.slice(0, 4)]); // Keep last 5 critical
    }
  });

  useEffect(() => {
    loadHealthData();
  }, [selectedTimeRange]);

  // Auto-clear old metrics
  useEffect(() => {
    const interval = setInterval(() => {
      const fiveMinutesAgo = Date.now() - 300000;
      setLiveHealthMetrics(prev =>
        prev.filter(metric => metric.timestamp.getTime() > fiveMinutesAgo)
      );
      setCriticalAlerts(prev =>
        prev.filter(alert => new Date(alert.timestamp).getTime() > fiveMinutesAgo)
      );
    }, 60000); // Check every minute

    return () => clearInterval(interval);
  }, []);

  const loadHealthData = async () => {
    try {
      setLoading(true);
      // If connected to real-time, most data comes through WebSocket
      if (!connected) {
        const [servicesData, metricsData, alertsData] = await Promise.all([
          digitalTwinAPI.getServiceHealth(),
          digitalTwinAPI.getPerformanceMetrics(selectedTimeRange),
          digitalTwinAPI.getHealthAlerts()
        ]);

        setServiceHealth(servicesData);
        setPerformanceMetrics(metricsData);
        setHealthAlerts(alertsData);
      } else {
        // Just load what's not available through real-time
        const [servicesData, alertsData] = await Promise.all([
          digitalTwinAPI.getServiceHealth(),
          digitalTwinAPI.getHealthAlerts()
        ]);

        setServiceHealth(servicesData);
        setHealthAlerts(alertsData);
      }
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      console.error('Failed to load health data:', err);
      setError('Failed to load system health data');
    } finally {
      setLoading(false);
    }
  };

  const getHealthDimensions = (): HealthDimension[] => {
    if (!systemHealth) return [];

    return [
      {
        name: 'Data Collection',
        score: systemHealth.dataCollection,
        status: systemHealth.dataCollection >= 80 ? 'healthy' : systemHealth.dataCollection >= 60 ? 'warning' : 'error',
        trend: 2,
        description: 'Data collection services performance',
        icon: <Database className="h-6 w-6" />
      },
      {
        name: 'Personal Twins',
        score: systemHealth.personalTwins,
        status: systemHealth.personalTwins >= 80 ? 'healthy' : systemHealth.personalTwins >= 60 ? 'warning' : 'error',
        trend: 1,
        description: 'Personal Digital Twins health',
        icon: <Users className="h-6 w-6" />
      },
      {
        name: 'Data Integrity',
        score: systemHealth.dataIntegrity,
        status: systemHealth.dataIntegrity >= 80 ? 'healthy' : systemHealth.dataIntegrity >= 60 ? 'warning' : 'error',
        trend: 0,
        description: 'Data quality and consistency',
        icon: <Shield className="h-6 w-6" />
      },
      {
        name: 'System Performance',
        score: systemHealth.performance,
        status: systemHealth.performance >= 80 ? 'healthy' : systemHealth.performance >= 60 ? 'warning' : 'error',
        trend: -1,
        description: 'Overall system performance',
        icon: <Gauge className="h-6 w-6" />
      },
      {
        name: 'AI Services',
        score: systemHealth.aiServices,
        status: systemHealth.aiServices >= 80 ? 'healthy' : systemHealth.aiServices >= 60 ? 'warning' : 'error',
        trend: 3,
        description: 'AI analysis and processing',
        icon: <Brain className="h-6 w-6" />
      },
      {
        name: 'Package Management',
        score: systemHealth.packageManagement,
        status: systemHealth.packageManagement >= 80 ? 'healthy' : systemHealth.packageManagement >= 60 ? 'warning' : 'error',
        trend: 1,
        description: 'Data package operations',
        icon: <Package className="h-6 w-6" />
      }
    ];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getTrendIcon = (trend: number) => {
    if (trend > 0) return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (trend < 0) return <TrendingDown className="h-4 w-4 text-red-500" />;
    return <Minus className="h-4 w-4 text-gray-500" />;
  };

  const getOverallHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPerformanceColor = (value: number, threshold: { good: number; warning: number }) => {
    if (value <= threshold.good) return 'text-green-600';
    if (value <= threshold.warning) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading && !systemHealth) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const healthDimensions = getHealthDimensions();

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">System Health Monitor</h2>
          <p className="text-gray-600">Digital Twin ecosystem health and performance</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="text-sm text-gray-500">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="15m">15 minutes</option>
            <option value="1h">1 hour</option>
            <option value="6h">6 hours</option>
            <option value="24h">24 hours</option>
            <option value="7d">7 days</option>
          </select>
          {/* Real-time Status */}
          <Badge className={connected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'} variant="secondary">
            {connected ? (
              <><Activity className="h-3 w-3 mr-1 animate-pulse" />Live</>
            ) : (
              <><WifiOff className="h-3 w-3 mr-1" />Offline</>
            )}
          </Badge>

          {/* Live Metrics Counter */}
          {liveHealthMetrics.length > 0 && (
            <Badge variant="outline" className="text-green-600">
              <TrendingUp className="h-3 w-3 mr-1" />
              {liveHealthMetrics.length} metrics
            </Badge>
          )}

          {/* Critical Alerts Counter */}
          {criticalAlerts.length > 0 && (
            <Badge variant="outline" className="text-red-600 animate-pulse">
              <AlertTriangle className="h-3 w-3 mr-1" />
              {criticalAlerts.length} critical
            </Badge>
          )}

          <Button variant="outline" size="sm" onClick={loadHealthData} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Health Alerts */}
      {healthAlerts.length > 0 && (
        <div className="space-y-2">
          {healthAlerts.slice(0, 3).map((alert, index) => (
            <Alert key={index} className={`border-${alert.severity === 'error' ? 'red' : alert.severity === 'warning' ? 'yellow' : 'blue'}-200 bg-${alert.severity === 'error' ? 'red' : alert.severity === 'warning' ? 'yellow' : 'blue'}-50`}>
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>{alert.title}</AlertTitle>
              <AlertDescription>{alert.message}</AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* Overall Health Score */}
      <Card>
        <CardContent className="p-6">
          <div className="text-center">
            <div className={`text-6xl font-bold ${getOverallHealthColor(systemHealth?.overallScore || 0)} mb-2`}>
              {systemHealth?.overallScore || 0}%
            </div>
            <div className="text-lg text-gray-600 mb-4">Overall Ecosystem Health</div>
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Heart className={`h-6 w-6 ${systemHealth?.overallScore >= 80 ? 'text-green-500' : systemHealth?.overallScore >= 60 ? 'text-yellow-500' : 'text-red-500'}`} />
              <Badge className={getStatusColor(systemHealth?.status || 'unknown')} variant="secondary">
                {systemHealth?.status || 'Unknown'}
              </Badge>
            </div>
            <Progress value={systemHealth?.overallScore || 0} className="w-64 mx-auto" />
          </div>
        </CardContent>
      </Card>

      {/* Health Dimensions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {healthDimensions.map((dimension, index) => (
          <Card key={index}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {dimension.icon}
                  <span className="font-medium">{dimension.name}</span>
                </div>
                {getTrendIcon(dimension.trend)}
              </div>

              <div className="mb-3">
                <div className={`text-2xl font-bold ${getOverallHealthColor(dimension.score)}`}>
                  {dimension.score}%
                </div>
                <Progress value={dimension.score} className="mt-2" />
              </div>

              <div className="flex items-center justify-between">
                <Badge className={getStatusColor(dimension.status)} variant="secondary">
                  {dimension.status}
                </Badge>
                <span className="text-xs text-gray-500">{dimension.description}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Detailed Metrics */}
      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-4">
          {performanceMetrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Clock className="h-5 w-5 text-blue-500" />
                    <span className="font-medium">Response Time</span>
                  </div>
                  <div className={`text-2xl font-bold ${getPerformanceColor(performanceMetrics.avgResponseTime, { good: 100, warning: 500 })}`}>
                    {performanceMetrics.avgResponseTime}ms
                  </div>
                  <div className="text-sm text-gray-600">Average response time</div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Zap className="h-5 w-5 text-green-500" />
                    <span className="font-medium">Throughput</span>
                  </div>
                  <div className="text-2xl font-bold text-green-600">
                    {performanceMetrics.requestsPerSecond}
                  </div>
                  <div className="text-sm text-gray-600">Requests per second</div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span className="font-medium">Success Rate</span>
                  </div>
                  <div className={`text-2xl font-bold ${getPerformanceColor(100 - performanceMetrics.errorRate, { good: 95, warning: 90 })}`}>
                    {(100 - performanceMetrics.errorRate).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Operation success rate</div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Activity className="h-5 w-5 text-purple-500" />
                    <span className="font-medium">Active Connections</span>
                  </div>
                  <div className="text-2xl font-bold text-purple-600">
                    {performanceMetrics.activeConnections}
                  </div>
                  <div className="text-sm text-gray-600">Current connections</div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Service Health Status</CardTitle>
              <CardDescription>Individual service health and performance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {serviceHealth.map((service, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-center space-x-4">
                      {getStatusIcon(service.status)}
                      <div>
                        <div className="font-medium">{service.name}</div>
                        <div className="text-sm text-gray-600">{service.endpoint}</div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-6">
                      <div className="text-center">
                        <div className="text-sm font-medium">{service.uptime}</div>
                        <div className="text-xs text-gray-500">Uptime</div>
                      </div>

                      <div className="text-center">
                        <div className="text-sm font-medium">{service.responseTime}ms</div>
                        <div className="text-xs text-gray-500">Response</div>
                      </div>

                      <div className="text-center">
                        <div className="text-sm font-medium">{service.memoryUsage}MB</div>
                        <div className="text-xs text-gray-500">Memory</div>
                      </div>

                      <div className="text-center">
                        <div className="text-sm font-medium">{service.cpuUsage}%</div>
                        <div className="text-xs text-gray-500">CPU</div>
                      </div>

                      <Badge className={getStatusColor(service.status)} variant="secondary">
                        {service.status}
                      </Badge>
                    </div>
                  </div>
                ))}

                {serviceHealth.length === 0 && (
                  <div className="text-center py-8">
                    <Server className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">No service data available</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resources" className="space-y-4">
          {performanceMetrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Cpu className="h-5 w-5" />
                    <span>CPU Usage</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Overall CPU</span>
                        <span className={getPerformanceColor(performanceMetrics.cpuUsage, { good: 70, warning: 85 })}>
                          {performanceMetrics.cpuUsage}%
                        </span>
                      </div>
                      <Progress value={performanceMetrics.cpuUsage} />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>System Load</span>
                        <span>{performanceMetrics.systemLoad}</span>
                      </div>
                      <Progress value={performanceMetrics.systemLoad * 20} />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <MemoryStick className="h-5 w-5" />
                    <span>Memory Usage</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Used Memory</span>
                        <span className={getPerformanceColor(performanceMetrics.memoryUsage, { good: 70, warning: 85 })}>
                          {performanceMetrics.memoryUsage}%
                        </span>
                      </div>
                      <Progress value={performanceMetrics.memoryUsage} />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Available</span>
                        <span>{performanceMetrics.availableMemory}GB</span>
                      </div>
                      <Progress value={100 - performanceMetrics.memoryUsage} />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <HardDrive className="h-5 w-5" />
                    <span>Disk Usage</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Used Space</span>
                        <span className={getPerformanceColor(performanceMetrics.diskUsage, { good: 70, warning: 85 })}>
                          {performanceMetrics.diskUsage}%
                        </span>
                      </div>
                      <Progress value={performanceMetrics.diskUsage} />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Available</span>
                        <span>{performanceMetrics.availableDisk}GB</span>
                      </div>
                      <Progress value={100 - performanceMetrics.diskUsage} />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Network className="h-5 w-5" />
                    <span>Network Activity</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Inbound</span>
                        <span>{performanceMetrics.networkIn} MB/s</span>
                      </div>
                      <Progress value={(performanceMetrics.networkIn / 100) * 100} />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Outbound</span>
                        <span>{performanceMetrics.networkOut} MB/s</span>
                      </div>
                      <Progress value={(performanceMetrics.networkOut / 100) * 100} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SystemHealthMonitor;