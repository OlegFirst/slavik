/**
 * AI Platform ISO 22301 - Main Dashboard
 * ======================================
 *
 * Real-time platform overview with NO MOCK DATA
 * All data from real AI Platform services
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { dashboardService, type DashboardData } from '@/services/realtime';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
  GitBranch,
  Loader2,
  Server,
  TrendingUp,
  Users,
  Wrench,
  BarChart3,
  Gauge,
  Eye,
} from 'lucide-react';

export const PlatformDashboard: React.FC = () => {
  const { data, isLoading, error, refetch } = useQuery<DashboardData>({
    queryKey: ['platform-dashboard'],
    queryFn: () => dashboardService.getDashboardData(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading platform data...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-red-50 to-orange-100">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertCircle className="w-6 h-6" />
              Error Loading Dashboard
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Unable to fetch platform data. Please ensure all services are running.
            </p>
            <Button onClick={() => refetch()}>Retry</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const healthPercentage = (data.services.healthy / data.services.total) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AI Platform ISO 22301</h1>
              <p className="text-gray-600">System Management Dashboard</p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" onClick={() => refetch()}>
                <Activity className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <div className="text-xs text-gray-500">
                Last updated: {new Date(data.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* Services Health Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <CheckCircle className="w-8 h-8" />
                <span className="text-4xl font-bold">{data.services.healthy}</span>
              </div>
              <p className="text-green-100">Healthy Services</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-500 to-orange-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <AlertCircle className="w-8 h-8" />
                <span className="text-4xl font-bold">{data.services.degraded}</span>
              </div>
              <p className="text-yellow-100">Degraded Services</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-red-500 to-pink-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <Server className="w-8 h-8" />
                <span className="text-4xl font-bold">{data.services.down}</span>
              </div>
              <p className="text-red-100">Down Services</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <Gauge className="w-8 h-8" />
                <span className="text-4xl font-bold">{Math.round(healthPercentage)}%</span>
              </div>
              <p className="text-blue-100">Health Score</p>
            </CardContent>
          </Card>
        </div>

        {/* Platform Health Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="w-5 h-5" />
              Platform Health Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Overall Health</span>
                <span className="text-sm font-bold">{Math.round(healthPercentage)}%</span>
              </div>
              <Progress value={healthPercentage} className="h-3" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {data.services.details.map((service) => (
                <div
                  key={service.service}
                  className="border rounded-lg p-3 flex items-center justify-between"
                >
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        service.status === 'healthy'
                          ? 'bg-green-500'
                          : service.status === 'degraded'
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                    />
                    <span className="text-sm font-medium capitalize">{service.service}</span>
                  </div>
                  {service.response_time_ms && (
                    <span className="text-xs text-gray-500">{service.response_time_ms}ms</span>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Workflows */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="w-5 h-5" />
                Workflows
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Workflows</span>
                  <span className="text-2xl font-bold">{data.workflows.total}</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-xl font-bold text-blue-600">{data.workflows.active}</div>
                    <div className="text-xs text-gray-600">Active</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-xl font-bold text-green-600">
                      {data.workflows.completed}
                    </div>
                    <div className="text-xs text-gray-600">Completed</div>
                  </div>
                  <div className="text-center p-3 bg-red-50 rounded-lg">
                    <div className="text-xl font-bold text-red-600">{data.workflows.failed}</div>
                    <div className="text-xs text-gray-600">Failed</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Community */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Community Intelligence
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Members</span>
                  <span className="text-2xl font-bold">{data.community.total_members}</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <div className="text-xl font-bold text-purple-600">
                      {data.community.active_members}
                    </div>
                    <div className="text-xs text-gray-600">Active</div>
                  </div>
                  <div className="text-center p-3 bg-indigo-50 rounded-lg">
                    <div className="text-xl font-bold text-indigo-600">
                      {data.community.total_contributions}
                    </div>
                    <div className="text-xs text-gray-600">Contributions</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI Insights */}
        {data.insights.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                AI Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {data.insights.slice(0, 5).map((insight, idx) => (
                  <div
                    key={idx}
                    className={`border-l-4 pl-4 py-2 ${
                      insight.severity === 'critical'
                        ? 'border-red-500 bg-red-50'
                        : insight.severity === 'high'
                        ? 'border-orange-500 bg-orange-50'
                        : insight.severity === 'medium'
                        ? 'border-yellow-500 bg-yellow-50'
                        : 'border-blue-500 bg-blue-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-xs font-medium text-gray-500 uppercase">
                          {insight.category}
                        </span>
                        <p className="text-sm font-medium mt-1">{insight.message}</p>
                      </div>
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          insight.severity === 'critical'
                            ? 'bg-red-200 text-red-800'
                            : insight.severity === 'high'
                            ? 'bg-orange-200 text-orange-800'
                            : insight.severity === 'medium'
                            ? 'bg-yellow-200 text-yellow-800'
                            : 'bg-blue-200 text-blue-800'
                        }`}
                      >
                        {insight.severity}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Link to="/tools">
                <Button variant="outline" className="w-full h-20 flex flex-col gap-2">
                  <Wrench className="w-6 h-6" />
                  <span className="text-sm">Tools ({data.tools.length})</span>
                </Button>
              </Link>
              <Link to="/metrics">
                <Button variant="outline" className="w-full h-20 flex flex-col gap-2">
                  <BarChart3 className="w-6 h-6" />
                  <span className="text-sm">Metrics</span>
                </Button>
              </Link>
              <Link to="/grafana">
                <Button variant="outline" className="w-full h-20 flex flex-col gap-2">
                  <Eye className="w-6 h-6" />
                  <span className="text-sm">Dashboards</span>
                </Button>
              </Link>
              <Link to="/architecture">
                <Button variant="outline" className="w-full h-20 flex flex-col gap-2">
                  <Server className="w-6 h-6" />
                  <span className="text-sm">Architecture</span>
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PlatformDashboard;
