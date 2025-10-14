import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  PieChart, Pie, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import {
  Server, Database, Activity, AlertTriangle, CheckCircle, Search,
  RefreshCw, Download, ExternalLink, Cpu, Network, HardDrive
} from 'lucide-react';
import { serviceCatalogAPI, ServiceInfo, CatalogStats } from '@/services/service-catalog';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];

export const ServiceCatalog: React.FC = () => {
  const [services, setServices] = useState<ServiceInfo[]>([]);
  const [stats, setStats] = useState<CatalogStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Load catalog data
  useEffect(() => {
    loadCatalogData();
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      loadCatalogData();
    }, 30000);

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const loadCatalogData = async () => {
    try {
      setLoading(true);
      const [servicesData, statsData] = await Promise.all([
        serviceCatalogAPI.getAllServices(),
        serviceCatalogAPI.getStats(),
      ]);

      setServices(servicesData.services);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load catalog data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthBadgeVariant = (health: string) => {
    switch (health) {
      case 'healthy':
        return 'default';
      case 'degraded':
        return 'secondary';
      case 'unhealthy':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const getRegistrationBadgeVariant = (status: string) => {
    switch (status) {
      case 'registered':
        return 'default';
      case 'not_registered':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active':
        return 'default';
      case 'configured':
        return 'secondary';
      case 'deprecated':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const filteredServices = services.filter(service => {
    const matchesSearch = service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      service.description?.toLowerCase().includes(searchTerm.toLowerCase());

    if (selectedTab === 'all') return matchesSearch;
    if (selectedTab === 'registered') return matchesSearch && service.registration_status === 'registered';
    if (selectedTab === 'missing') return matchesSearch && service.registration_status === 'not_registered';
    if (selectedTab === 'healthy') return matchesSearch && service.health_status === 'healthy';
    if (selectedTab === 'unhealthy') return matchesSearch && service.health_status === 'unhealthy';

    return matchesSearch;
  });

  const exportData = () => {
    const dataStr = JSON.stringify({ services, stats }, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

    const exportFileDefaultName = `service_catalog_${new Date().toISOString()}.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Prepare chart data
  const typeChartData = stats ? Object.entries(stats.by_type).map(([name, value]) => ({
    name: name.split('/').pop() || name,
    value
  })) : [];

  const statusChartData = stats ? Object.entries(stats.by_status).map(([name, value]) => ({
    name,
    value
  })) : [];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Service Catalog</h1>
          <p className="text-gray-600 mt-1">
            Unified view of all platform services (catalog + runtime)
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Badge variant={autoRefresh ? 'default' : 'outline'}>
            {autoRefresh ? 'Auto-refresh: ON' : 'Auto-refresh: OFF'}
          </Badge>
          <Button
            onClick={() => setAutoRefresh(!autoRefresh)}
            variant="outline"
            size="sm"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
          <Button onClick={loadCatalogData} variant="outline" size="sm" disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button onClick={exportData} variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Services</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totals.total_services}</div>
              <p className="text-xs text-muted-foreground mt-2">
                Services in catalog
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Running Services</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {stats.totals.registered_services}
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Currently registered
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Coverage</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.totals.coverage_percent.toFixed(1)}%
              </div>
              <Progress value={stats.totals.coverage_percent} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-2">
                Catalog services running
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Health</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {stats.totals.healthy_services}
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Healthy services
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Charts */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Services by Type</CardTitle>
              <CardDescription>Distribution across platform layers</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={typeChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {typeChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Services by Status</CardTitle>
              <CardDescription>Active, configured, deprecated, archived</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={statusChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#00C49F" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Services Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Services</CardTitle>
              <CardDescription>
                {filteredServices.length} of {services.length} services
              </CardDescription>
            </div>
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search services..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8 w-64"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-4">
            <TabsList>
              <TabsTrigger value="all">All ({services.length})</TabsTrigger>
              <TabsTrigger value="registered">
                Running ({services.filter(s => s.registration_status === 'registered').length})
              </TabsTrigger>
              <TabsTrigger value="missing">
                Missing ({services.filter(s => s.registration_status === 'not_registered').length})
              </TabsTrigger>
              <TabsTrigger value="healthy">
                Healthy ({services.filter(s => s.health_status === 'healthy').length})
              </TabsTrigger>
              <TabsTrigger value="unhealthy">
                Unhealthy ({services.filter(s => s.health_status === 'unhealthy').length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value={selectedTab} className="space-y-4">
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Port</TableHead>
                      <TableHead>Registration</TableHead>
                      <TableHead>Health</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Business Process</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredServices.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                          No services found
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredServices.map((service) => (
                        <TableRow key={service.name}>
                          <TableCell className="font-medium">
                            <div className="flex items-center gap-2">
                              <Server className="w-4 h-4" />
                              {service.name}
                            </div>
                          </TableCell>
                          <TableCell>
                            <span className="text-sm text-muted-foreground">
                              {service.type.split('/').pop()}
                            </span>
                          </TableCell>
                          <TableCell>
                            {service.actual_port || service.expected_port || '-'}
                          </TableCell>
                          <TableCell>
                            <Badge variant={getRegistrationBadgeVariant(service.registration_status)}>
                              {service.registration_status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={getHealthBadgeVariant(service.health_status)}>
                              {service.health_status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={getStatusBadgeVariant(service.status)}>
                              {service.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <span className="text-sm">
                              {service.business_process || '-'}
                            </span>
                          </TableCell>
                          <TableCell className="text-right">
                            <Button variant="ghost" size="sm">
                              <ExternalLink className="w-4 h-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Metadata */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Catalog Metadata</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Platform</dt>
                <dd className="text-lg font-semibold">{stats.metadata.platform_name}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Version</dt>
                <dd className="text-lg font-semibold">{stats.metadata.version}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Schema Version</dt>
                <dd className="text-lg font-semibold">{stats.metadata.schema_version}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Last Updated</dt>
                <dd className="text-lg font-semibold">
                  {new Date(stats.metadata.generated_at).toLocaleString()}
                </dd>
              </div>
            </dl>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
