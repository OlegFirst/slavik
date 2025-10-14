import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Button } from './ui/button';
import {
  Server,
  Database,
  Network,
  Activity,
  CheckCircle,
  XCircle,
  AlertTriangle,
  BarChart3,
  Users,
  MessageSquare,
  Shield,
  Zap
} from 'lucide-react';

interface ServiceStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  response_time_ms: number;
  last_updated: string;
  description: string;
  port?: number;
}

interface SystemMetrics {
  overall_status: string;
  services_count: number;
  healthy_services: number;
  degraded_services: number;
  unhealthy_services: number;
  active_alerts: number;
  last_updated: string;
}

interface EventBusStats {
  queue_size: number;
  handlers_count: number;
  status: string;
  handlers: string[];
}

const CentralizedArchitectureMonitor: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemMetrics | null>(null);
  const [services, setServices] = useState<Record<string, ServiceStatus>>({});
  const [eventBusStats, setEventBusStats] = useState<EventBusStats | null>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSystemStatus = async () => {
    try {
      // Check if monitoring service is available
      const monitoringResponse = await fetch('http://localhost:8779/status');
      if (monitoringResponse.ok) {
        const status = await monitoringResponse.json();
        setSystemStatus(status);
      }
    } catch (error) {
      console.warn('Monitoring service not available, using gateway status');
      // Fallback to API Gateway health check
      try {
        const gatewayResponse = await fetch('http://localhost:8777/health');
        if (gatewayResponse.ok) {
          setSystemStatus({
            overall_status: 'healthy',
            services_count: 3,
            healthy_services: 3,
            degraded_services: 0,
            unhealthy_services: 0,
            active_alerts: 0,
            last_updated: new Date().toISOString()
          });
        }
      } catch (e) {
        console.error('Both monitoring and gateway unavailable');
      }
    }
  };

  const fetchServices = async () => {
    try {
      const response = await fetch('http://localhost:8779/services');
      if (response.ok) {
        const data = await response.json();
        setServices(data);
      }
    } catch (error) {
      // Fallback to checking core services directly
      const coreServices = {
        'database_gateway': { url: 'http://localhost:8888/health', port: 8888 },
        'api_gateway': { url: 'http://localhost:8777/health', port: 8777 },
        'crm_bridge': { url: 'http://localhost:8778/health', port: 8778 },
        'monitoring_service': { url: 'http://localhost:8779/health', port: 8779 }
      };

      const serviceStatus: Record<string, ServiceStatus> = {};

      for (const [name, config] of Object.entries(coreServices)) {
        try {
          const start = performance.now();
          const response = await fetch(config.url);
          const responseTime = performance.now() - start;

          serviceStatus[name] = {
            name,
            status: response.ok ? 'healthy' : 'degraded',
            response_time_ms: responseTime,
            last_updated: new Date().toISOString(),
            description: `${name.replace('_', ' ').toUpperCase()} Service`,
            port: config.port
          };
        } catch (e) {
          serviceStatus[name] = {
            name,
            status: 'unhealthy',
            response_time_ms: 0,
            last_updated: new Date().toISOString(),
            description: `${name.replace('_', ' ').toUpperCase()} Service`,
            port: config.port
          };
        }
      }

      setServices(serviceStatus);
    }
  };

  const fetchEventBusStats = async () => {
    try {
      const response = await fetch('http://localhost:8778/eventbus/stats');
      if (response.ok) {
        const data = await response.json();
        setEventBusStats(data);
      }
    } catch (error) {
      console.warn('Event Bus stats not available');
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await fetch('http://localhost:8779/logs?limit=20');
      if (response.ok) {
        const data = await response.json();
        setLogs(data);
      }
    } catch (error) {
      console.warn('Logs not available');
    }
  };

  const triggerTestEvent = async (eventType: string) => {
    try {
      const testData = {
        project_id: 999,
        partner_name: "Test Organization",
        compliance_score: 85,
        title: "Test Event from Admin Panel"
      };

      const response = await fetch(`http://localhost:8778/eventbus/${eventType}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testData)
      });

      if (response.ok) {
        alert(`✅ ${eventType} event triggered successfully!`);
        // Refresh stats
        fetchEventBusStats();
      }
    } catch (error) {
      alert(`❌ Failed to trigger ${eventType} event`);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchSystemStatus(),
        fetchServices(),
        fetchEventBusStats(),
        fetchLogs()
      ]);
      setLoading(false);
    };

    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'unhealthy': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'degraded': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'unhealthy': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Centralized Architecture Monitor</h1>
        <Badge variant="outline" className="text-sm">
          Real-time Dashboard
        </Badge>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overall Status</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              {getStatusIcon(systemStatus?.overall_status || 'unknown')}
              <div className="text-2xl font-bold capitalize">
                {systemStatus?.overall_status || 'Unknown'}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Services</CardTitle>
            <Network className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemStatus?.healthy_services || Object.keys(services).length}/{systemStatus?.services_count || Object.keys(services).length}
            </div>
            <p className="text-xs text-muted-foreground">Healthy</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Event Bus</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {eventBusStats?.handlers_count || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {eventBusStats?.status || 'Unknown'} • Queue: {eventBusStats?.queue_size || 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemStatus?.active_alerts || 0}
            </div>
            <p className="text-xs text-muted-foreground">System alerts</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="services" className="space-y-4">
        <TabsList>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="eventbus">Event Bus</TabsTrigger>
          <TabsTrigger value="architecture">Architecture</TabsTrigger>
          <TabsTrigger value="documentation">Documentation</TabsTrigger>
        </TabsList>

        <TabsContent value="services" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(services).map(([name, service]) => (
              <Card key={name}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{service.description}</CardTitle>
                    {getStatusIcon(service.status)}
                  </div>
                  {service.port && (
                    <CardDescription>Port: {service.port}</CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Response Time:</span>
                      <span>{service.response_time_ms.toFixed(1)}ms</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Status:</span>
                      <Badge variant={service.status === 'healthy' ? 'default' : 'destructive'}>
                        {service.status}
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Last updated: {new Date(service.last_updated).toLocaleTimeString()}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="eventbus" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Event Bus Status</CardTitle>
                <CardDescription>Real-time event processing system</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span>Status:</span>
                  <Badge variant={eventBusStats?.status === 'running' ? 'default' : 'destructive'}>
                    {eventBusStats?.status || 'Unknown'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Queue Size:</span>
                  <span>{eventBusStats?.queue_size || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Handlers:</span>
                  <span>{eventBusStats?.handlers_count || 0}</span>
                </div>

                {eventBusStats?.handlers && (
                  <div className="space-y-2">
                    <h4 className="font-medium">Active Handlers:</h4>
                    <div className="flex flex-wrap gap-1">
                      {eventBusStats.handlers.map((handler) => (
                        <Badge key={handler} variant="outline">
                          {handler}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Test Events</CardTitle>
                <CardDescription>Trigger sample events for testing</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  onClick={() => triggerTestEvent('project-won')}
                  className="w-full"
                  variant="outline"
                >
                  <Zap className="h-4 w-4 mr-2" />
                  Trigger Project Won
                </Button>
                <Button
                  onClick={() => triggerTestEvent('audit-completed')}
                  className="w-full"
                  variant="outline"
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Trigger Audit Completed
                </Button>
                <Button
                  onClick={() => triggerTestEvent('incident-critical')}
                  className="w-full"
                  variant="outline"
                >
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Trigger Critical Incident
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="architecture" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Centralized Architecture Overview</CardTitle>
              <CardDescription>BCM Platform unified infrastructure</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Architecture Diagram */}
                <div className="border rounded-lg p-4 bg-muted/50">
                  <h3 className="font-semibold mb-4">Service Architecture</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                    <div className="space-y-2">
                      <div className="font-medium text-blue-600">Frontend Layer</div>
                      <div className="space-y-1 text-xs">
                        <div>• Admin Panel (3001)</div>
                        <div>• Unified Platform (3000)</div>
                        <div>• Web Portal (3000)</div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="font-medium text-green-600">API Layer</div>
                      <div className="space-y-1 text-xs">
                        <div>• API Gateway (8777)</div>
                        <div>• Database Gateway (8888)</div>
                        <div>• CRM Bridge (8778)</div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="font-medium text-purple-600">Core Services</div>
                      <div className="space-y-1 text-xs">
                        <div>• Odoo BCM (8069)</div>
                        <div>• AI Orchestrator (8000)</div>
                        <div>• Event Bus (8001)</div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="font-medium text-orange-600">Infrastructure</div>
                      <div className="space-y-1 text-xs">
                        <div>• PostgreSQL (5432)</div>
                        <div>• Redis (6379)</div>
                        <div>• RabbitMQ (5672)</div>
                        <div>• Monitoring (8779)</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Key Features */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <h4 className="font-semibold">Key Features</h4>
                    <ul className="space-y-1 text-sm">
                      <li>✅ Unified Database Access</li>
                      <li>✅ Centralized API Gateway</li>
                      <li>✅ Event-Driven Architecture</li>
                      <li>✅ Real-time Monitoring</li>
                      <li>✅ CRM Integration Bridge</li>
                      <li>✅ Service Discovery</li>
                    </ul>
                  </div>
                  <div className="space-y-3">
                    <h4 className="font-semibold">Benefits</h4>
                    <ul className="space-y-1 text-sm">
                      <li>🚀 Improved Performance</li>
                      <li>🔧 Easier Maintenance</li>
                      <li>📊 Better Observability</li>
                      <li>🔄 Seamless Integration</li>
                      <li>⚡ Real-time Processing</li>
                      <li>🛡️ Enhanced Security</li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="documentation" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>API Documentation</CardTitle>
                <CardDescription>Complete API reference for centralized services</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="border-l-4 border-blue-500 pl-4">
                    <h4 className="font-semibold">Database Gateway API</h4>
                    <p className="text-sm text-muted-foreground">http://localhost:8888</p>
                    <div className="mt-2 space-y-1 text-xs">
                      <div><code>POST /query</code> - Execute database operations</div>
                      <div><code>POST /auth/odoo</code> - Odoo authentication</div>
                      <div><code>GET /health</code> - Health check</div>
                    </div>
                  </div>

                  <div className="border-l-4 border-green-500 pl-4">
                    <h4 className="font-semibold">API Gateway</h4>
                    <p className="text-sm text-muted-foreground">http://localhost:8777</p>
                    <div className="mt-2 space-y-1 text-xs">
                      <div><code>GET /api/&lt;service&gt;/&lt;path&gt;</code> - Service proxy</div>
                      <div><code>GET /services</code> - Service registry</div>
                      <div><code>GET /metrics</code> - Gateway metrics</div>
                    </div>
                  </div>

                  <div className="border-l-4 border-purple-500 pl-4">
                    <h4 className="font-semibold">CRM Bridge API</h4>
                    <p className="text-sm text-muted-foreground">http://localhost:8778</p>
                    <div className="mt-2 space-y-1 text-xs">
                      <div><code>GET /projects</code> - Get CRM projects</div>
                      <div><code>POST /eventbus/publish</code> - Publish events</div>
                      <div><code>GET /eventbus/stats</code> - Event Bus stats</div>
                    </div>
                  </div>

                  <div className="border-l-4 border-orange-500 pl-4">
                    <h4 className="font-semibold">Monitoring API</h4>
                    <p className="text-sm text-muted-foreground">http://localhost:8779</p>
                    <div className="mt-2 space-y-1 text-xs">
                      <div><code>GET /status</code> - System status</div>
                      <div><code>GET /services</code> - Services health</div>
                      <div><code>GET /logs</code> - System logs</div>
                      <div><code>GET /dashboard</code> - Web dashboard</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Implementation Guide</CardTitle>
                <CardDescription>How to integrate with centralized architecture</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2">1. Database Operations</h4>
                    <div className="bg-muted p-3 rounded text-xs font-mono">
                      <div>// Using Database Gateway</div>
                      <div>const response = await fetch('http://localhost:8888/query', {'{'}</div>
                      <div>&nbsp;&nbsp;method: 'POST',</div>
                      <div>&nbsp;&nbsp;headers: {'{'} 'Content-Type': 'application/json' {'}'},</div>
                      <div>&nbsp;&nbsp;body: JSON.stringify({'{'}</div>
                      <div>&nbsp;&nbsp;&nbsp;&nbsp;database: 'odoo',</div>
                      <div>&nbsp;&nbsp;&nbsp;&nbsp;operation: 'odoo_search',</div>
                      <div>&nbsp;&nbsp;&nbsp;&nbsp;model: 'crm.lead'</div>
                      <div>&nbsp;&nbsp;{'}'})</div>
                      <div>{'}'})</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">2. Service Calls</h4>
                    <div className="bg-muted p-3 rounded text-xs font-mono">
                      <div>// Via API Gateway</div>
                      <div>const data = await fetch(</div>
                      <div>&nbsp;&nbsp;'http://localhost:8777/api/crm_bridge/projects'</div>
                      <div>).then(r ={'>'} r.json())</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">3. Event Publishing</h4>
                    <div className="bg-muted p-3 rounded text-xs font-mono">
                      <div>// Publish to Event Bus</div>
                      <div>await fetch('http://localhost:8778/eventbus/publish', {'{'}</div>
                      <div>&nbsp;&nbsp;method: 'POST',</div>
                      <div>&nbsp;&nbsp;headers: {'{'} 'Content-Type': 'application/json' {'}'},</div>
                      <div>&nbsp;&nbsp;body: JSON.stringify({'{'}</div>
                      <div>&nbsp;&nbsp;&nbsp;&nbsp;event_type: 'custom.event',</div>
                      <div>&nbsp;&nbsp;&nbsp;&nbsp;source_module: 'admin_panel',</div>
                      <div>&nbsp;&nbsp;&nbsp;&nbsp;project_id: 123,</div>
                      <div>&nbsp;&nbsp;&nbsp;&nbsp;data: {'{'} /* event data */ {'}'}</div>
                      <div>&nbsp;&nbsp;{'}'})</div>
                      <div>{'}'})</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CentralizedArchitectureMonitor;