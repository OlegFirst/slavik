/**
 * Grafana Dashboard Viewer
 * =========================
 *
 * Embed and view Grafana dashboards directly in the UI
 * Real integration with Grafana server
 */

import React, { useState } from 'react';
import { grafanaService } from '@/services/realtime';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ExternalLink, Maximize2, Minimize2, RefreshCw } from 'lucide-react';

interface Dashboard {
  id: string;
  name: string;
  description: string;
}

const DASHBOARDS: Dashboard[] = [
  {
    id: 'platform-overview',
    name: 'Platform Overview',
    description: 'Overall platform health and metrics',
  },
  {
    id: 'service-orchestrator',
    name: 'AI Orchestrator',
    description: 'AI Orchestrator service metrics',
  },
  {
    id: 'service-workflow',
    name: 'Workflow Intelligence',
    description: 'Workflow execution and performance',
  },
  {
    id: 'service-community',
    name: 'Community Intelligence',
    description: 'Community metrics and engagement',
  },
  {
    id: 'service-predictive',
    name: 'Predictive Service',
    description: 'ML model performance and predictions',
  },
  {
    id: 'service-analytics',
    name: 'Analytics Specialist',
    description: 'Analytics tools and insights',
  },
];

export const GrafanaViewer: React.FC = () => {
  const [selectedDashboard, setSelectedDashboard] = useState<string>('platform-overview');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const openInNewTab = () => {
    const url = grafanaService.getDashboardURL(selectedDashboard, {
      theme,
      refresh: '30s',
    });
    window.open(url, '_blank');
  };

  const dashboardURL = grafanaService.getDashboardURL(selectedDashboard, {
    theme,
    kiosk: true,
    refresh: '30s',
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Grafana Dashboards</h1>
          <p className="text-gray-600">Real-time metrics visualization</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={theme} onValueChange={(value: 'light' | 'dark') => setTheme(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="light">Light</SelectItem>
              <SelectItem value="dark">Dark</SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={openInNewTab}
          >
            <ExternalLink className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <Tabs value={selectedDashboard} onValueChange={setSelectedDashboard}>
        <TabsList className="grid grid-cols-6 w-full">
          {DASHBOARDS.map((dashboard) => (
            <TabsTrigger key={dashboard.id} value={dashboard.id}>
              {dashboard.name}
            </TabsTrigger>
          ))}
        </TabsList>

        {DASHBOARDS.map((dashboard) => (
          <TabsContent key={dashboard.id} value={dashboard.id} className="mt-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{dashboard.name}</CardTitle>
                    <p className="text-sm text-gray-600 mt-1">{dashboard.description}</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div
                  className={`relative bg-gray-100 rounded-lg overflow-hidden ${
                    isFullscreen ? 'fixed inset-0 z-50 rounded-none' : ''
                  }`}
                  style={{ height: isFullscreen ? '100vh' : '800px' }}
                >
                  <iframe
                    key={refreshKey}
                    src={dashboardURL}
                    width="100%"
                    height="100%"
                    frameBorder="0"
                    className="w-full h-full"
                    title={dashboard.name}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* Quick Links */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Links</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {DASHBOARDS.map((dashboard) => (
              <button
                key={dashboard.id}
                onClick={() => setSelectedDashboard(dashboard.id)}
                className={`p-4 border rounded-lg text-left transition-all hover:shadow-md ${
                  selectedDashboard === dashboard.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <h3 className="font-semibold text-gray-900">{dashboard.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{dashboard.description}</p>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Grafana Server Info */}
      <Card>
        <CardHeader>
          <CardTitle>Grafana Connection</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">
                Connected to Grafana server at <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:3000</code>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Dashboards auto-refresh every 30 seconds
              </p>
            </div>
            <a
              href="http://localhost:3000"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
            >
              Open Grafana
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GrafanaViewer;
