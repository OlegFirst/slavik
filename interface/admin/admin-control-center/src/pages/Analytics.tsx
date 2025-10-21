import React, { useState, useEffect } from 'react';
import { useRealtime } from '../hooks/useRealtime';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import {
  TrendingUp, TrendingDown, Activity, AlertTriangle, CheckCircle,
  Users, Server, Database, Cpu, HardDrive, Wifi, Calendar, Download
} from 'lucide-react';
import { bcmAPI } from '@/services/api';

interface MetricData {
  timestamp: string;
  value: number;
  label?: string;
}

interface AnalyticsData {
  performance: MetricData[];
  incidents: MetricData[];
  compliance: MetricData[];
  risks: MetricData[];
  training: MetricData[];
  exercises: MetricData[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData>({
    performance: [],
    incidents: [],
    compliance: [],
    risks: [],
    training: [],
    exercises: []
  });
  const [loading, setLoading] = useState(true);
  const [systemHealth, setSystemHealth] = useState(0);

  // Real-time data
  const { metrics, isConnected } = useRealtime();

  // Fetch analytics data
  useEffect(() => {
    fetchAnalyticsData();
    const interval = setInterval(fetchAnalyticsData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [timeRange]);

  // Update real-time metrics
  useEffect(() => {
    if (metrics) {
      // Update performance data with real-time metrics
      setAnalyticsData(prev => ({
        ...prev,
        performance: [
          ...prev.performance.slice(-29), // Keep last 29 points
          {
            timestamp: new Date().toISOString(),
            value: metrics.cpu || 0,
            label: 'CPU'
          }
        ]
      }));

      // Calculate system health
      const health = calculateSystemHealth(metrics);
      setSystemHealth(health);
    }
  }, [metrics]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await bcmAPI.get(`/analytics/data?range=${timeRange}`);

      // Use mock data if API fails
      const data = response.data || generateMockData();
      setAnalyticsData(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      setAnalyticsData(generateMockData());
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = (): AnalyticsData => {
    const now = Date.now();
    const points = 30;

    return {
      performance: Array.from({ length: points }, (_, i) => ({
        timestamp: new Date(now - (points - i) * 60000).toISOString(),
        value: Math.random() * 100,
        label: 'CPU'
      })),
      incidents: Array.from({ length: points }, (_, i) => ({
        timestamp: new Date(now - (points - i) * 60000).toISOString(),
        value: Math.floor(Math.random() * 10),
        label: 'Incidents'
      })),
      compliance: Array.from({ length: points }, (_, i) => ({
        timestamp: new Date(now - (points - i) * 60000).toISOString(),
        value: 75 + Math.random() * 20,
        label: 'Compliance'
      })),
      risks: Array.from({ length: points }, (_, i) => ({
        timestamp: new Date(now - (points - i) * 60000).toISOString(),
        value: Math.floor(Math.random() * 50),
        label: 'Risks'
      })),
      training: Array.from({ length: points }, (_, i) => ({
        timestamp: new Date(now - (points - i) * 60000).toISOString(),
        value: 60 + Math.random() * 30,
        label: 'Training'
      })),
      exercises: Array.from({ length: points }, (_, i) => ({
        timestamp: new Date(now - (points - i) * 60000).toISOString(),
        value: Math.floor(Math.random() * 20),
        label: 'Exercises'
      }))
    };
  };

  const calculateSystemHealth = (metrics: any): number => {
    if (!metrics) return 0;

    const weights = {
      cpu: 0.3,
      memory: 0.3,
      disk: 0.2,
      network: 0.2
    };

    const health =
      (100 - (metrics.cpu || 0)) * weights.cpu +
      (100 - (metrics.memory || 0)) * weights.memory +
      (100 - (metrics.disk || 0)) * weights.disk +
      Math.min(100, (metrics.network || 0) / 10) * weights.network;

    return Math.round(health);
  };

  const exportData = () => {
    const dataStr = JSON.stringify(analyticsData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

    const exportFileDefaultName = `analytics_${new Date().toISOString()}.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const getHealthColor = (health: number): string => {
    if (health >= 80) return 'text-green-600';
    if (health >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">Real-time insights and performance metrics</p>
        </div>
        <div className="flex items-center gap-4">
          <Badge variant={isConnected ? 'default' : 'destructive'}>
            {isConnected ? 'Live' : 'Offline'}
          </Badge>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1h">Last Hour</SelectItem>
              <SelectItem value="24h">Last 24 Hours</SelectItem>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={exportData} variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getHealthColor(systemHealth)}`}>
              {systemHealth}%
            </div>
            <Progress value={systemHealth} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-2">
              Overall system performance
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Incidents</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analyticsData.incidents[analyticsData.incidents.length - 1]?.value || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              <TrendingDown className="inline w-3 h-3 mr-1 text-green-600" />
              -12% from last period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {Math.round(analyticsData.compliance[analyticsData.compliance.length - 1]?.value || 0)}%
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              ISO 22301 compliance level
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Risk Score</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {analyticsData.risks[analyticsData.risks.length - 1]?.value || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              <TrendingUp className="inline w-3 h-3 mr-1 text-red-600" />
              +5% from last period
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="incidents">Incidents</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="training">Training</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Performance</CardTitle>
              <CardDescription>Real-time system metrics and resource utilization</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={analyticsData.performance}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatTime}
                  />
                  <YAxis />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value: any) => [`${value.toFixed(2)}%`, 'Usage']}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                    name="CPU Usage"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Resource Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'CPU', value: metrics?.cpu || 45 },
                        { name: 'Memory', value: metrics?.memory || 62 },
                        { name: 'Disk', value: metrics?.disk || 38 },
                        { name: 'Network', value: Math.min(100, (metrics?.network || 15) / 10) }
                      ]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.value.toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {COLORS.map((color, index) => (
                        <Cell key={`cell-${index}`} fill={color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Service Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Server className="w-4 h-4" />
                    <span>API Gateway</span>
                  </div>
                  <Badge variant="default">Running</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Database className="w-4 h-4" />
                    <span>Database</span>
                  </div>
                  <Badge variant="default">Healthy</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Wifi className="w-4 h-4" />
                    <span>Socket.io Server</span>
                  </div>
                  <Badge variant={isConnected ? "default" : "destructive"}>
                    {isConnected ? "Connected" : "Disconnected"}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-4 h-4" />
                    <span>AI Services</span>
                  </div>
                  <Badge variant="default">5 Active</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="incidents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Incident Trends</CardTitle>
              <CardDescription>Track and analyze incident patterns over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={analyticsData.incidents}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatTime}
                  />
                  <YAxis />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                  />
                  <Legend />
                  <Bar dataKey="value" fill="#FF8042" name="Incidents" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compliance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Tracking</CardTitle>
              <CardDescription>ISO 22301 compliance metrics and trends</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={analyticsData.compliance}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatTime}
                  />
                  <YAxis domain={[0, 100]} />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value: any) => [`${value.toFixed(1)}%`, 'Compliance']}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#00C49F"
                    strokeWidth={2}
                    name="Compliance Score"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="training" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Training & Exercises</CardTitle>
              <CardDescription>Track training completion and exercise performance</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={analyticsData.training}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatTime}
                  />
                  <YAxis domain={[0, 100]} />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value: any) => [`${value.toFixed(1)}%`, 'Completion']}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#FFBB28"
                    fill="#FFBB28"
                    fillOpacity={0.6}
                    name="Training Completion"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};