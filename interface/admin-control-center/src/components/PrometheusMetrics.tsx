/**
 * Prometheus Metrics Viewer
 * ==========================
 *
 * Display real-time metrics from Prometheus
 * NO MOCK DATA - Direct Prometheus integration
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { prometheusService } from '@/services/realtime';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  Activity,
  Cpu,
  HardDrive,
  Network,
  Clock,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Loader2,
} from 'lucide-react';

export const PrometheusMetrics: React.FC = () => {
  // Fetch system metrics
  const { data: systemMetrics, isLoading } = useQuery({
    queryKey: ['prometheus-metrics'],
    queryFn: () => prometheusService.getSystemMetrics(),
    refetchInterval: 5000, // Refresh every 5 seconds for real-time feel
  });

  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const getStatusColor = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return 'text-red-600';
    if (value >= thresholds.warning) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getProgressColor = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return 'bg-red-500';
    if (value >= thresholds.warning) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!systemMetrics) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-gray-500">
            <AlertTriangle className="w-12 h-12 mx-auto mb-2" />
            <p>Unable to fetch Prometheus metrics</p>
            <p className="text-sm">Ensure Prometheus is running on port 9090</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const services = Object.keys(systemMetrics.cpu);

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Average CPU */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <Cpu className="w-5 h-5 text-blue-500" />
              <span className="text-2xl font-bold">
                {Object.values(systemMetrics.cpu).length > 0
                  ? Math.round(
                      Object.values(systemMetrics.cpu).reduce((a, b) => a + b, 0) /
                        Object.values(systemMetrics.cpu).length
                    )
                  : 0}
                %
              </span>
            </div>
            <p className="text-sm text-gray-600">Avg CPU Usage</p>
          </CardContent>
        </Card>

        {/* Average Memory */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <HardDrive className="w-5 h-5 text-purple-500" />
              <span className="text-2xl font-bold">
                {Object.values(systemMetrics.memory).length > 0
                  ? Math.round(
                      Object.values(systemMetrics.memory).reduce((a, b) => a + b, 0) /
                        Object.values(systemMetrics.memory).length
                    )
                  : 0}
                MB
              </span>
            </div>
            <p className="text-sm text-gray-600">Avg Memory</p>
          </CardContent>
        </Card>

        {/* Total Request Rate */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <Activity className="w-5 h-5 text-green-500" />
              <span className="text-2xl font-bold">
                {Object.values(systemMetrics.requestRate).reduce((a, b) => a + b, 0).toFixed(1)}
              </span>
            </div>
            <p className="text-sm text-gray-600">Requests/sec</p>
          </CardContent>
        </Card>

        {/* Error Rate */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              <span className="text-2xl font-bold">
                {Object.values(systemMetrics.errorRate).reduce((a, b) => a + b, 0).toFixed(2)}
              </span>
            </div>
            <p className="text-sm text-gray-600">Errors/sec</p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Metrics by Service */}
      <Tabs defaultValue="cpu" className="w-full">
        <TabsList>
          <TabsTrigger value="cpu">
            <Cpu className="w-4 h-4 mr-2" />
            CPU
          </TabsTrigger>
          <TabsTrigger value="memory">
            <HardDrive className="w-4 h-4 mr-2" />
            Memory
          </TabsTrigger>
          <TabsTrigger value="requests">
            <Activity className="w-4 h-4 mr-2" />
            Requests
          </TabsTrigger>
          <TabsTrigger value="uptime">
            <Clock className="w-4 h-4 mr-2" />
            Uptime
          </TabsTrigger>
        </TabsList>

        {/* CPU Tab */}
        <TabsContent value="cpu" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>CPU Usage by Service</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {services.map((service) => {
                  const cpu = systemMetrics.cpu[service] || 0;
                  return (
                    <div key={service}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">{service}</span>
                        <span
                          className={`text-sm font-bold ${getStatusColor(cpu, {
                            warning: 70,
                            critical: 90,
                          })}`}
                        >
                          {cpu}%
                        </span>
                      </div>
                      <Progress
                        value={cpu}
                        className={`h-2 ${getProgressColor(cpu, { warning: 70, critical: 90 })}`}
                      />
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Memory Tab */}
        <TabsContent value="memory" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Memory Usage by Service</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {services.map((service) => {
                  const memory = systemMetrics.memory[service] || 0;
                  return (
                    <div key={service}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">{service}</span>
                        <span className="text-sm font-bold text-gray-900">{memory} MB</span>
                      </div>
                      <Progress value={Math.min((memory / 1024) * 100, 100)} className="h-2" />
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Requests Tab */}
        <TabsContent value="requests" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Request Rate by Service</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {services.map((service) => {
                  const requestRate = systemMetrics.requestRate[service] || 0;
                  const errorRate = systemMetrics.errorRate[service] || 0;
                  const errorPercentage =
                    requestRate > 0 ? (errorRate / requestRate) * 100 : 0;

                  return (
                    <div key={service} className="border-b pb-4 last:border-0">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">{service}</span>
                        <div className="flex items-center gap-4">
                          <span className="text-sm text-green-600 flex items-center gap-1">
                            <TrendingUp className="w-3 h-3" />
                            {requestRate.toFixed(2)} req/s
                          </span>
                          {errorRate > 0 && (
                            <span className="text-sm text-red-600 flex items-center gap-1">
                              <TrendingDown className="w-3 h-3" />
                              {errorRate.toFixed(2)} err/s
                            </span>
                          )}
                        </div>
                      </div>
                      {errorPercentage > 0 && (
                        <div className="flex items-center gap-2">
                          <Progress
                            value={errorPercentage}
                            className="h-1 bg-red-100"
                            style={{ '--progress-color': 'red' } as any}
                          />
                          <span className="text-xs text-red-600">{errorPercentage.toFixed(1)}% errors</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Uptime Tab */}
        <TabsContent value="uptime" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Service Uptime</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {services.map((service) => {
                  const uptime = systemMetrics.uptime[service] || 0;
                  return (
                    <div key={service} className="border rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Clock className="w-4 h-4 text-blue-500" />
                        <span className="font-medium text-sm">{service}</span>
                      </div>
                      <div className="text-2xl font-bold text-gray-900">
                        {formatUptime(uptime)}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{uptime.toLocaleString()} seconds</div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Metrics Timestamp */}
      <div className="text-center text-xs text-gray-500">
        Last updated: {new Date(systemMetrics.timestamp).toLocaleString()}
      </div>
    </div>
  );
};

export default PrometheusMetrics;
