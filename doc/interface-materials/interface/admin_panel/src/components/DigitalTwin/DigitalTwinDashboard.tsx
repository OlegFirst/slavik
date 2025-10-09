import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Users,
  Brain,
  Activity,
  Database,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Zap,
  RefreshCw,
  Settings,
  Eye,
  Network,
  Clock,
  BarChart3,
  Shield,
  Package,
  Server,
  Wifi,
  WifiOff,
  Signal,
  SignalHigh,
  SignalLow,
  SignalMedium
} from 'lucide-react';
import { digitalTwinAPI, DigitalTwinOverview, PersonalTwin, SystemHealth } from '@/services/digitalTwinAPI';
import { useDigitalTwin, useRealTimeMetrics } from '@/contexts/DigitalTwinContext';

interface DigitalTwinDashboardProps {
  className?: string;
}

const DigitalTwinDashboard: React.FC<DigitalTwinDashboardProps> = ({ className }) => {
  const {
    overview,
    systemHealth,
    connectionStatus,
    isLive,
    toggleLive,
    refreshData,
    lastError,
    clearError
  } = useDigitalTwin();

  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [realtimeEvents, setRealtimeEvents] = useState<any[]>([]);

  // Real-time metrics subscription
  useRealTimeMetrics('dashboard_update', (data) => {
    setRealtimeEvents(prev => [
      { ...data, timestamp: new Date(), id: Date.now() },
      ...prev.slice(0, 9) // Keep last 10 events
    ]);
    setLastUpdate(new Date());
  });

  // Update timestamp when data changes
  useEffect(() => {
    if (overview || systemHealth) {
      setLastUpdate(new Date());
    }
  }, [overview, systemHealth]);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      await refreshData();
      setLastUpdate(new Date());
      clearError();
    } catch (err) {
      console.error('Failed to refresh data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getConnectionIcon = () => {
    if (!connectionStatus.connected) {
      return <WifiOff className="h-4 w-4 text-red-500" />;
    }

    const latency = connectionStatus.latency || 0;
    if (latency < 100) return <SignalHigh className="h-4 w-4 text-green-500" />;
    if (latency < 300) return <SignalMedium className="h-4 w-4 text-yellow-500" />;
    return <SignalLow className="h-4 w-4 text-red-500" />;
  };

  const getConnectionStatus = () => {
    if (!connectionStatus.connected) {
      return {
        text: `Offline (${connectionStatus.reconnectAttempts} retries)`,
        color: 'text-red-600 bg-red-100'
      };
    }

    const latency = connectionStatus.latency;
    if (latency) {
      return {
        text: `Live (${latency}ms)`,
        color: latency < 100 ? 'text-green-600 bg-green-100' :
               latency < 300 ? 'text-yellow-600 bg-yellow-100' :
               'text-red-600 bg-red-100'
      };
    }

    return {
      text: 'Connected',
      color: 'text-green-600 bg-green-100'
    };
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'error':
      case 'inactive':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'error':
      case 'inactive':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading && !overview) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Digital Twin Management</h1>
          <div className="flex space-x-2">
            <Button disabled>
              <RefreshCw className="h-4 w-4 animate-spin mr-2" />
              Loading...
            </Button>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-6 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  const connectionStatusInfo = getConnectionStatus();

  return (
    <div className={`p-6 space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Digital Twin Management</h1>
          <p className="text-gray-600 mt-1">
            Monitor and manage the Digital Twin ecosystem
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="text-sm text-gray-500">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>

          {/* Connection Status Indicator */}
          <div className="flex items-center space-x-1">
            {getConnectionIcon()}
            <Badge className={connectionStatusInfo.color} variant="secondary">
              {connectionStatusInfo.text}
            </Badge>
          </div>

          {/* Real-time Events Counter */}
          {realtimeEvents.length > 0 && (
            <Badge variant="outline" className="text-blue-600">
              <Activity className="h-3 w-3 mr-1" />
              {realtimeEvents.length} live events
            </Badge>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={toggleLive}
            className={isLive ? 'bg-green-50 border-green-200' : 'bg-gray-50'}
          >
            {isLive ? <Wifi className="h-4 w-4" /> : <WifiOff className="h-4 w-4" />}
            {isLive ? 'Live' : 'Manual'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {lastError && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Connection Error</AlertTitle>
          <AlertDescription>
            {lastError}
            <Button
              variant="ghost"
              size="sm"
              onClick={clearError}
              className="ml-2 h-6 px-2"
            >
              Dismiss
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Connection Status Alert */}
      {!connectionStatus.connected && isLive && (
        <Alert className="border-yellow-200 bg-yellow-50">
          <Wifi className="h-4 w-4" />
          <AlertTitle>Real-time Connection Lost</AlertTitle>
          <AlertDescription>
            Attempting to reconnect... ({connectionStatus.reconnectAttempts} attempts)
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.location.reload()}
              className="ml-2 h-6 px-2"
            >
              Reload Page
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Overview Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Personal Twins</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overview?.personalTwins.total || 0}</div>
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <Badge className={getStatusColor('active')} variant="secondary">
                {overview?.personalTwins.active || 0} active
              </Badge>
              <Badge className={getStatusColor('inactive')} variant="secondary">
                {overview?.personalTwins.inactive || 0} inactive
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Organizational Twins</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overview?.organizationalTwins.total || 0}</div>
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <Badge className={getStatusColor('healthy')} variant="secondary">
                {overview?.organizationalTwins.healthy || 0} healthy
              </Badge>
              <Badge className={getStatusColor('warning')} variant="secondary">
                {overview?.organizationalTwins.warning || 0} warning
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Collection</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {overview?.dataCollection.activeServices || 0}/{overview?.dataCollection.totalServices || 0}
            </div>
            <div className="text-xs text-muted-foreground">
              Services collecting data
            </div>
            <Progress
              value={(overview?.dataCollection.activeServices || 0) / (overview?.dataCollection.totalServices || 1) * 100}
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold flex items-center">
              {systemHealth?.overallScore || 0}%
              {getStatusIcon(systemHealth?.status || 'unknown')}
            </div>
            <div className="text-xs text-muted-foreground">
              Overall ecosystem health
            </div>
            <Progress value={systemHealth?.overallScore || 0} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="personal">Personal Twins</TabsTrigger>
          <TabsTrigger value="collection">Data Collection</TabsTrigger>
          <TabsTrigger value="packages">Packages</TabsTrigger>
          <TabsTrigger value="health">System Health</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* Real-time Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <Clock className="h-5 w-5 mr-2" />
                  Real-time Activity
                </div>
                {connectionStatus.connected && (
                  <Badge className="bg-green-100 text-green-700 animate-pulse">
                    <Activity className="h-3 w-3 mr-1" />
                    Live
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {/* Real-time events first */}
                {realtimeEvents.map((event, index) => (
                  <div key={event.id} className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                    <Activity className="h-4 w-4 text-blue-500 animate-pulse" />
                    <div className="flex-1">
                      <div className="font-medium">{event.title || 'Real-time Update'}</div>
                      <div className="text-sm text-gray-600">{event.description || `${event.type} event received`}</div>
                    </div>
                    <div className="text-xs text-blue-600">Live • {event.timestamp.toLocaleTimeString()}</div>
                  </div>
                ))}

                {/* Historical activity */}
                {overview?.recentActivity?.map((activity, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    {getStatusIcon(activity.type)}
                    <div className="flex-1">
                      <div className="font-medium">{activity.title}</div>
                      <div className="text-sm text-gray-600">{activity.description}</div>
                    </div>
                    <div className="text-xs text-gray-500">{activity.timestamp}</div>
                  </div>
                )) || (
                  realtimeEvents.length === 0 && (
                    <div className="text-center text-gray-500 py-4">
                      {connectionStatus.connected ? 'Waiting for real-time events...' : 'No recent activity'}
                    </div>
                  )
                )}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Zap className="h-5 w-5 mr-2" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Button className="h-20 flex flex-col" variant="outline">
                  <Users className="h-6 w-6 mb-2" />
                  Sync All Twins
                </Button>
                <Button className="h-20 flex flex-col" variant="outline">
                  <Database className="h-6 w-6 mb-2" />
                  Force Collection
                </Button>
                <Button className="h-20 flex flex-col" variant="outline">
                  <Package className="h-6 w-6 mb-2" />
                  Package Export
                </Button>
                <Button className="h-20 flex flex-col" variant="outline">
                  <Settings className="h-6 w-6 mb-2" />
                  System Config
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="personal" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Personal Twins Management</CardTitle>
              <CardDescription>
                Manage individual user Digital Twins
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Users className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600">Personal Twin Manager will be loaded here</p>
                <Button className="mt-4" onClick={() => window.location.hash = '#personal-twins'}>
                  Open Personal Twin Manager
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="collection" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Data Collection Monitor</CardTitle>
              <CardDescription>
                Monitor all {overview?.dataCollection.totalServices || 0} data collection services
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Network className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600">Data Collection Monitor will be loaded here</p>
                <Button className="mt-4" onClick={() => window.location.hash = '#data-collection'}>
                  Open Collection Monitor
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="packages" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Package Management</CardTitle>
              <CardDescription>
                Manage TwinDataPackages and transport
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Package className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600">Package Manager will be loaded here</p>
                <Button className="mt-4" onClick={() => window.location.hash = '#packages'}>
                  Open Package Manager
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="health" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Health Monitor</CardTitle>
              <CardDescription>
                Overall Digital Twin ecosystem health
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Health Overview */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {systemHealth?.overallScore || 0}%
                    </div>
                    <div className="text-sm text-gray-600">Overall Score</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {systemHealth?.connectedServices || 0}
                    </div>
                    <div className="text-sm text-gray-600">Connected Services</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {systemHealth?.dataIntegrity || 0}%
                    </div>
                    <div className="text-sm text-gray-600">Data Integrity</div>
                  </div>
                </div>

                {/* Service Status */}
                <div>
                  <h4 className="font-medium mb-3">Core Services Status</h4>
                  <div className="space-y-2">
                    {systemHealth?.services?.map((service, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(service.status)}
                          <span className="font-medium">{service.name}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(service.status)} variant="secondary">
                            {service.status}
                          </Badge>
                          <span className="text-sm text-gray-500">{service.responseTime}ms</span>
                        </div>
                      </div>
                    )) || (
                      <div className="text-center text-gray-500 py-4">
                        No service data available
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DigitalTwinDashboard;