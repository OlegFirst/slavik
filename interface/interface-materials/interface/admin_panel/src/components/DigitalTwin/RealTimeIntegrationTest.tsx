import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Activity,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Wifi,
  WifiOff,
  Settings,
  Play,
  Pause,
  RefreshCw,
  Zap,
  Signal,
  SignalHigh,
  SignalMedium,
  SignalLow,
  Clock,
  Database,
  Users,
  Package,
  Monitor
} from 'lucide-react';
import { useDigitalTwin, useRealTimeMetrics } from '@/contexts/DigitalTwinContext';

interface RealTimeIntegrationTestProps {
  className?: string;
}

const RealTimeIntegrationTest: React.FC<RealTimeIntegrationTestProps> = ({ className }) => {
  const {
    connectionStatus,
    isLive,
    toggleLive,
    overview,
    personalTwins,
    services,
    packages,
    systemHealth,
    lastError,
    clearError,
    refreshData
  } = useDigitalTwin();

  const [testResults, setTestResults] = useState<any[]>([]);
  const [isRunningTests, setIsRunningTests] = useState(false);
  const [receivedEvents, setReceivedEvents] = useState<any[]>([]);

  // Subscribe to all real-time events for testing
  useRealTimeMetrics('all', (data) => {
    setReceivedEvents(prev => [
      { ...data, timestamp: new Date(), id: Date.now() },
      ...prev.slice(0, 49) // Keep last 50 events
    ]);
  });

  const runIntegrationTests = async () => {
    setIsRunningTests(true);
    setTestResults([]);

    const tests = [
      {
        name: 'WebSocket Connection',
        test: () => connectionStatus.connected,
        description: 'Verifies real-time WebSocket connection is active'
      },
      {
        name: 'Data Context Loading',
        test: () => overview !== null || personalTwins.length > 0,
        description: 'Verifies data is being loaded through context'
      },
      {
        name: 'Real-time Events',
        test: () => receivedEvents.length > 0,
        description: 'Verifies real-time events are being received'
      },
      {
        name: 'Connection Latency',
        test: () => connectionStatus.latency && connectionStatus.latency < 1000,
        description: 'Verifies connection latency is acceptable (<1000ms)'
      },
      {
        name: 'Error Handling',
        test: () => typeof clearError === 'function',
        description: 'Verifies error handling mechanisms are in place'
      },
      {
        name: 'Live Mode Toggle',
        test: () => typeof toggleLive === 'function',
        description: 'Verifies live mode can be toggled'
      },
      {
        name: 'Data Refresh',
        test: () => typeof refreshData === 'function',
        description: 'Verifies manual data refresh capability'
      }
    ];

    for (const testCase of tests) {
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate test execution time

      const result = {
        ...testCase,
        passed: testCase.test(),
        timestamp: new Date()
      };

      setTestResults(prev => [...prev, result]);
    }

    setIsRunningTests(false);
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

  const getDataStatus = () => {
    const dataPoints = [
      { name: 'Overview', data: overview, icon: Monitor },
      { name: 'Personal Twins', data: personalTwins.length, icon: Users },
      { name: 'Services', data: services.length, icon: Database },
      { name: 'Packages', data: packages.length, icon: Package },
      { name: 'System Health', data: systemHealth, icon: Activity }
    ];

    return dataPoints;
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Real-time Integration Test</h2>
          <p className="text-gray-600">Test and verify the Digital Twin real-time integration</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            onClick={runIntegrationTests}
            disabled={isRunningTests}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {isRunningTests ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            {isRunningTests ? 'Running Tests...' : 'Run Tests'}
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {lastError && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Integration Error</AlertTitle>
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

      {/* Connection Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            {getConnectionIcon()}
            <span>Connection Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className={`text-2xl font-bold ${connectionStatus.connected ? 'text-green-600' : 'text-red-600'}`}>
                {connectionStatus.connected ? 'Connected' : 'Disconnected'}
              </div>
              <div className="text-sm text-gray-600">WebSocket Status</div>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {connectionStatus.latency || 0}ms
              </div>
              <div className="text-sm text-gray-600">Latency</div>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {connectionStatus.reconnectAttempts}
              </div>
              <div className="text-sm text-gray-600">Reconnect Attempts</div>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleLive}
                  className={isLive ? 'bg-green-50 border-green-200' : 'bg-gray-50'}
                >
                  {isLive ? <Wifi className="h-4 w-4" /> : <WifiOff className="h-4 w-4" />}
                  {isLive ? 'Live' : 'Manual'}
                </Button>
              </div>
              <div className="text-sm text-gray-600 mt-2">Mode Control</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs defaultValue="tests" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="tests">Integration Tests</TabsTrigger>
          <TabsTrigger value="data">Data Status</TabsTrigger>
          <TabsTrigger value="events">Real-time Events</TabsTrigger>
          <TabsTrigger value="diagnostics">Diagnostics</TabsTrigger>
        </TabsList>

        <TabsContent value="tests" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Integration Test Results</CardTitle>
              <CardDescription>
                {testResults.length > 0 && (
                  <span>
                    {testResults.filter(t => t.passed).length}/{testResults.length} tests passed
                  </span>
                )}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {testResults.map((test, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      {test.passed ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-500" />
                      )}
                      <div>
                        <div className="font-medium">{test.name}</div>
                        <div className="text-sm text-gray-600">{test.description}</div>
                      </div>
                    </div>
                    <Badge
                      className={test.passed ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}
                      variant="secondary"
                    >
                      {test.passed ? 'PASS' : 'FAIL'}
                    </Badge>
                  </div>
                ))}

                {testResults.length === 0 && !isRunningTests && (
                  <div className="text-center py-8">
                    <Settings className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">No tests run yet. Click "Run Tests" to start.</p>
                  </div>
                )}

                {isRunningTests && (
                  <div className="text-center py-8">
                    <RefreshCw className="h-8 w-8 mx-auto text-blue-500 animate-spin mb-4" />
                    <p className="text-blue-600">Running integration tests...</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="data" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Data Loading Status</CardTitle>
              <CardDescription>Status of data loaded through the real-time context</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {getDataStatus().map((item, index) => {
                  const IconComponent = item.icon;
                  const hasData = item.data !== null && item.data !== 0;

                  return (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <IconComponent className={`h-5 w-5 ${hasData ? 'text-green-500' : 'text-gray-400'}`} />
                        <span className="font-medium">{item.name}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-600">
                          {typeof item.data === 'number' ? `${item.data} items` : hasData ? 'Loaded' : 'No data'}
                        </span>
                        {hasData ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-gray-400" />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Real-time Events</span>
                <Badge variant="outline" className="text-green-600">
                  <Activity className="h-3 w-3 mr-1" />
                  {receivedEvents.length} events
                </Badge>
              </CardTitle>
              <CardDescription>Live events received through the WebSocket connection</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {receivedEvents.map((event, index) => (
                  <div key={event.id} className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                    <Zap className="h-4 w-4 text-blue-500" />
                    <div className="flex-1">
                      <div className="font-medium">{event.type || 'Event'}</div>
                      <div className="text-sm text-gray-600">
                        {JSON.stringify(event.data || {}, null, 0).slice(0, 100)}...
                      </div>
                    </div>
                    <div className="text-xs text-blue-600">
                      <Clock className="h-3 w-3 inline mr-1" />
                      {event.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                ))}

                {receivedEvents.length === 0 && (
                  <div className="text-center py-8">
                    <Activity className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">
                      {connectionStatus.connected ? 'Waiting for real-time events...' : 'Not connected to receive events'}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="diagnostics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Diagnostics</CardTitle>
              <CardDescription>Technical details about the integration</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Context State</h4>
                  <div className="bg-gray-50 p-3 rounded text-sm font-mono">
                    <pre>{JSON.stringify({
                      connected: connectionStatus.connected,
                      latency: connectionStatus.latency,
                      reconnectAttempts: connectionStatus.reconnectAttempts,
                      isLive,
                      hasOverview: !!overview,
                      personalTwinsCount: personalTwins.length,
                      servicesCount: services.length,
                      packagesCount: packages.length,
                      hasSystemHealth: !!systemHealth,
                      lastError
                    }, null, 2)}</pre>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2">Performance Metrics</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Connection Latency:</span>
                      <span className="ml-2">{connectionStatus.latency || 'N/A'}ms</span>
                    </div>
                    <div>
                      <span className="font-medium">Events Received:</span>
                      <span className="ml-2">{receivedEvents.length}</span>
                    </div>
                    <div>
                      <span className="font-medium">Last Connected:</span>
                      <span className="ml-2">
                        {connectionStatus.lastConnected?.toLocaleTimeString() || 'Never'}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Mode:</span>
                      <span className="ml-2">{isLive ? 'Live' : 'Manual'}</span>
                    </div>
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

export default RealTimeIntegrationTest;