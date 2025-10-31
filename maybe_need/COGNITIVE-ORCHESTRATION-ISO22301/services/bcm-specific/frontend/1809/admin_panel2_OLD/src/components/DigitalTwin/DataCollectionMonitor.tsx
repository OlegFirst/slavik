import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Network,
  Database,
  Activity,
  Search,
  RefreshCw,
  Settings,
  Eye,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  Server,
  Wifi,
  WifiOff,
  BarChart3,
  Filter,
  Download,
  Upload,
  Play,
  Pause,
  Square,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';
import { digitalTwinAPI, DataCollectionService, ServiceMetrics, CollectionStats } from '@/services/digitalTwinAPI';
import { useDataCollectionServices, useRealTimeMetrics } from '@/contexts/DigitalTwinContext';

interface DataCollectionMonitorProps {
  className?: string;
}

interface ServiceGroup {
  name: string;
  services: DataCollectionService[];
  totalServices: number;
  activeServices: number;
  errorServices: number;
}

const DataCollectionMonitor: React.FC<DataCollectionMonitorProps> = ({ className }) => {
  const { services, connected } = useDataCollectionServices();
  const [filteredServices, setFilteredServices] = useState<DataCollectionService[]>([]);
  const [serviceGroups, setServiceGroups] = useState<ServiceGroup[]>([]);
  const [collectionStats, setCollectionStats] = useState<CollectionStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [liveServiceUpdates, setLiveServiceUpdates] = useState<Map<string, any>>(new Map());
  const [realtimeMetrics, setRealtimeMetrics] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedService, setSelectedService] = useState<DataCollectionService | null>(null);
  const [serviceMetrics, setServiceMetrics] = useState<ServiceMetrics | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Real-time service status updates
  useRealTimeMetrics('service_status_update', (data) => {
    setLiveServiceUpdates(prev => {
      const updated = new Map(prev);
      updated.set(data.serviceId, {
        ...data,
        timestamp: new Date()
      });
      return updated;
    });
  });

  // Real-time performance metrics
  useRealTimeMetrics('service_performance', (data) => {
    setRealtimeMetrics(prev => [
      { ...data, timestamp: new Date(), id: Date.now() },
      ...prev.slice(0, 49) // Keep last 50 metrics
    ]);
  });

  // Real-time collection statistics
  useRealTimeMetrics('collection_stats', (data) => {
    setCollectionStats(data);
  });

  // Auto-clear old service updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveServiceUpdates(prev => {
        const updated = new Map();
        const oneMinuteAgo = Date.now() - 60000;

        prev.forEach((update, serviceId) => {
          if (update.timestamp.getTime() > oneMinuteAgo) {
            updated.set(serviceId, update);
          }
        });

        return updated;
      });
    }, 10000); // Check every 10 seconds

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    filterServices();
    groupServices();
  }, [services, searchTerm, statusFilter]);

  const loadServices = async () => {
    try {
      setLoading(true);
      // If connected to real-time, services are automatically updated
      if (!connected) {
        const [servicesData, statsData] = await Promise.all([
          digitalTwinAPI.getDataCollectionServices(),
          digitalTwinAPI.getCollectionStats()
        ]);
        setCollectionStats(statsData);
      }
      setError(null);
    } catch (err) {
      console.error('Failed to load data collection services:', err);
      setError('Failed to load data collection services');
    } finally {
      setLoading(false);
    }
  };

  const filterServices = () => {
    let filtered = services;

    if (searchTerm) {
      filtered = filtered.filter(service =>
        service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        service.endpoint.toLowerCase().includes(searchTerm.toLowerCase()) ||
        service.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(service => service.status === statusFilter);
    }

    setFilteredServices(filtered);
  };

  const groupServices = () => {
    const groups: { [key: string]: DataCollectionService[] } = {};

    services.forEach(service => {
      if (!groups[service.category]) {
        groups[service.category] = [];
      }
      groups[service.category].push(service);
    });

    const groupsArray = Object.entries(groups).map(([name, groupServices]) => ({
      name,
      services: groupServices,
      totalServices: groupServices.length,
      activeServices: groupServices.filter(s => s.status === 'active').length,
      errorServices: groupServices.filter(s => s.status === 'error').length
    }));

    setServiceGroups(groupsArray);
  };

  const handleServiceAction = async (serviceId: string, action: string) => {
    try {
      setLoading(true);
      switch (action) {
        case 'start':
          await digitalTwinAPI.startDataCollection(serviceId);
          break;
        case 'stop':
          await digitalTwinAPI.stopDataCollection(serviceId);
          break;
        case 'restart':
          await digitalTwinAPI.restartDataCollection(serviceId);
          break;
        case 'configure':
          // Open configuration dialog
          break;
      }
      await loadServices();
    } catch (err) {
      console.error(`Failed to ${action} service:`, err);
      setError(`Failed to ${action} service`);
    } finally {
      setLoading(false);
    }
  };

  const handleViewMetrics = async (service: DataCollectionService) => {
    try {
      setSelectedService(service);
      setLoading(true);
      const metrics = await digitalTwinAPI.getServiceMetrics(service.id);
      setServiceMetrics(metrics);
      setIsDetailsOpen(true);
    } catch (err) {
      console.error('Failed to load service metrics:', err);
      setError('Failed to load service metrics');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'inactive':
        return <XCircle className="h-4 w-4 text-gray-500" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'inactive':
        return 'text-gray-600 bg-gray-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getTrendIcon = (trend: number) => {
    if (trend > 0) return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (trend < 0) return <TrendingDown className="h-4 w-4 text-red-500" />;
    return <Minus className="h-4 w-4 text-gray-500" />;
  };

  if (loading && services.length === 0) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="space-y-3">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Data Collection Monitor</h2>
          <p className="text-gray-600">Monitor all {services.length} data collection services</p>
        </div>
        <div className="flex items-center space-x-2">
          {/* Real-time Status */}
          <Badge className={connected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'} variant="secondary">
            {connected ? (
              <><Activity className="h-3 w-3 mr-1 animate-pulse" />Live ({services.length} services)</>
            ) : (
              <><WifiOff className="h-3 w-3 mr-1" />Offline</>
            )}
          </Badge>

          {/* Live Updates Counter */}
          {liveServiceUpdates.size > 0 && (
            <Badge variant="outline" className="text-blue-600">
              <Activity className="h-3 w-3 mr-1" />
              {liveServiceUpdates.size} live updates
            </Badge>
          )}

          {/* Real-time Metrics Counter */}
          {realtimeMetrics.length > 0 && (
            <Badge variant="outline" className="text-purple-600">
              <BarChart3 className="h-3 w-3 mr-1" />
              {realtimeMetrics.length} metrics
            </Badge>
          )}

          <Button variant="outline" onClick={loadServices} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Export
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

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Server className="h-8 w-8 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">{services.length}</div>
                <div className="text-sm text-gray-600">Total Services</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-8 w-8 text-green-500" />
              <div>
                <div className="text-2xl font-bold">
                  {services.filter(s => s.status === 'active').length}
                </div>
                <div className="text-sm text-gray-600">Active</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-8 w-8 text-red-500" />
              <div>
                <div className="text-2xl font-bold">
                  {services.filter(s => s.status === 'error').length}
                </div>
                <div className="text-sm text-gray-600">Errors</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Database className="h-8 w-8 text-purple-500" />
              <div>
                <div className="text-2xl font-bold">
                  {collectionStats?.totalDataPoints?.toLocaleString() || 0}
                </div>
                <div className="text-sm text-gray-600">Data Points</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Collection Performance */}
      {collectionStats && (
        <Card>
          <CardHeader>
            <CardTitle>Collection Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <div className="text-lg font-bold flex items-center">
                  {collectionStats.collectionsPerHour.toLocaleString()}
                  {getTrendIcon(collectionStats.hourlyTrend)}
                </div>
                <div className="text-sm text-gray-600">Collections per hour</div>
                <Progress value={75} className="mt-2" />
              </div>

              <div>
                <div className="text-lg font-bold flex items-center">
                  {collectionStats.avgResponseTime}ms
                  {getTrendIcon(collectionStats.responseTrend)}
                </div>
                <div className="text-sm text-gray-600">Avg response time</div>
                <Progress value={65} className="mt-2" />
              </div>

              <div>
                <div className="text-lg font-bold flex items-center">
                  {collectionStats.successRate}%
                  {getTrendIcon(collectionStats.successTrend)}
                </div>
                <div className="text-sm text-gray-600">Success rate</div>
                <Progress value={collectionStats.successRate} className="mt-2" />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search services by name, endpoint, or category..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex space-x-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="error">Error</option>
                <option value="warning">Warning</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Service Groups */}
      <Tabs defaultValue="list" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="list">Service List</TabsTrigger>
          <TabsTrigger value="groups">By Category</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Data Collection Services ({filteredServices.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {filteredServices.map((service) => (
                  <div key={service.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-center space-x-4 flex-1">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(service.status)}
                        <Badge className={getStatusColor(service.status)} variant="secondary">
                          {service.status}
                        </Badge>
                      </div>

                      <div className="flex-1">
                        <div className="font-medium">{service.name}</div>
                        <div className="text-sm text-gray-600">{service.endpoint}</div>
                        <div className="text-xs text-gray-500">Category: {service.category}</div>
                      </div>

                      <div className="text-center">
                        <div className="text-sm font-medium">{service.collectionsPerMinute}</div>
                        <div className="text-xs text-gray-500">per min</div>
                      </div>

                      <div className="text-center">
                        <div className="text-sm font-medium">{service.responseTime}ms</div>
                        <div className="text-xs text-gray-500">response</div>
                      </div>

                      <div className="text-center">
                        <div className="text-sm font-medium">{service.errorRate}%</div>
                        <div className="text-xs text-gray-500">error rate</div>
                      </div>

                      <div className="text-center">
                        <div className="text-sm font-medium">{service.lastCollection}</div>
                        <div className="text-xs text-gray-500">last collection</div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleViewMetrics(service)}
                      >
                        <BarChart3 className="h-4 w-4" />
                      </Button>

                      {service.status === 'active' ? (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleServiceAction(service.id, 'stop')}
                        >
                          <Pause className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleServiceAction(service.id, 'start')}
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleServiceAction(service.id, 'restart')}
                      >
                        <RefreshCw className="h-4 w-4" />
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleServiceAction(service.id, 'configure')}
                      >
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}

                {filteredServices.length === 0 && (
                  <div className="text-center py-8">
                    <Network className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">No services found</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="groups" className="space-y-4">
          {serviceGroups.map((group) => (
            <Card key={group.name}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>{group.name} ({group.totalServices})</span>
                  <div className="flex space-x-2">
                    <Badge className="bg-green-100 text-green-700">
                      {group.activeServices} active
                    </Badge>
                    {group.errorServices > 0 && (
                      <Badge className="bg-red-100 text-red-700">
                        {group.errorServices} errors
                      </Badge>
                    )}
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {group.services.map((service) => (
                    <div key={service.id} className="p-3 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-sm">{service.name}</span>
                        {getStatusIcon(service.status)}
                      </div>
                      <div className="text-xs text-gray-600 mb-2">{service.endpoint}</div>
                      <div className="flex justify-between text-xs">
                        <span>{service.collectionsPerMinute}/min</span>
                        <span>{service.responseTime}ms</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>

      {/* Service Metrics Modal */}
      <Dialog open={isDetailsOpen} onOpenChange={setIsDetailsOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Service Metrics - {selectedService?.name}</span>
            </DialogTitle>
            <DialogDescription>
              Detailed performance metrics and configuration
            </DialogDescription>
          </DialogHeader>

          {serviceMetrics && (
            <div className="space-y-6">
              {/* Performance Metrics */}
              <div>
                <h4 className="font-medium mb-3">Performance Metrics</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-blue-600">
                      {serviceMetrics.requestsPerSecond}
                    </div>
                    <div className="text-xs text-gray-600">Requests/sec</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-green-600">
                      {serviceMetrics.avgResponseTime}ms
                    </div>
                    <div className="text-xs text-gray-600">Avg Response</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-purple-600">
                      {serviceMetrics.successRate}%
                    </div>
                    <div className="text-xs text-gray-600">Success Rate</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-orange-600">
                      {serviceMetrics.dataPointsCollected?.toLocaleString()}
                    </div>
                    <div className="text-xs text-gray-600">Data Points</div>
                  </div>
                </div>
              </div>

              {/* Error Log */}
              {serviceMetrics.recentErrors && serviceMetrics.recentErrors.length > 0 && (
                <div>
                  <h4 className="font-medium mb-3">Recent Errors</h4>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {serviceMetrics.recentErrors.map((error, index) => (
                      <div key={index} className="p-2 bg-red-50 border border-red-200 rounded text-sm">
                        <div className="font-medium text-red-800">{error.message}</div>
                        <div className="text-red-600 text-xs">{error.timestamp}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Configuration */}
              <div>
                <h4 className="font-medium mb-3">Configuration</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Collection Interval:</span>
                    <span className="ml-2">{serviceMetrics.collectionInterval}ms</span>
                  </div>
                  <div>
                    <span className="font-medium">Timeout:</span>
                    <span className="ml-2">{serviceMetrics.timeout}ms</span>
                  </div>
                  <div>
                    <span className="font-medium">Retry Count:</span>
                    <span className="ml-2">{serviceMetrics.retryCount}</span>
                  </div>
                  <div>
                    <span className="font-medium">Buffer Size:</span>
                    <span className="ml-2">{serviceMetrics.bufferSize}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DataCollectionMonitor;