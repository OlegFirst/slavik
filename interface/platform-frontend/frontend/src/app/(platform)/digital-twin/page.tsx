'use client';

import React, { useState } from 'react';
import {
  Network,
  Activity,
  Box,
  Database,
  Search,
  Filter,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle,
  Server,
  Zap,
  GitBranch,
  Play,
  ChevronRight
} from 'lucide-react';

type ServiceStatus = 'production' | 'development' | 'disabled' | 'unknown';
type HealthStatus = 'healthy' | 'degraded' | 'down' | 'unknown';

interface PlatformService {
  name: string;
  port: number;
  status: ServiceStatus;
  health: HealthStatus;
  category: string;
  description: string;
  url: string;
}

// Service data from config
const platformServices: PlatformService[] = [
  // Infrastructure
  { name: 'Auth Service', port: 8001, status: 'production', health: 'healthy', category: 'Infrastructure', description: 'Authentication & authorization', url: 'http://localhost:8001' },
  { name: 'API Gateway', port: 8080, status: 'production', health: 'healthy', category: 'Infrastructure', description: 'Unified API entry point', url: 'http://localhost:8080' },
  { name: 'Event Bus', port: 8055, status: 'production', health: 'healthy', category: 'Infrastructure', description: 'Event-driven messaging', url: 'http://localhost:8055' },
  { name: 'WebSocket', port: 8056, status: 'production', health: 'healthy', category: 'Infrastructure', description: 'Real-time communications', url: 'ws://localhost:8056' },

  // BCM Core
  { name: 'BIA Service', port: 8012, status: 'production', health: 'healthy', category: 'BCM Core', description: 'Business Impact Analysis', url: 'http://localhost:8012' },
  { name: 'Planning Service', port: 8011, status: 'production', health: 'healthy', category: 'BCM Core', description: 'BC/DR Planning', url: 'http://localhost:8011' },
  { name: 'Risk Service', port: 8026, status: 'development', health: 'degraded', category: 'BCM Core', description: 'Risk Management', url: 'http://localhost:8026' },
  { name: 'Response Service', port: 8027, status: 'development', health: 'unknown', category: 'BCM Core', description: 'Incident Response', url: 'http://localhost:8027' },

  // Operations
  { name: 'Learning Service', port: 8021, status: 'production', health: 'healthy', category: 'Operations', description: 'Training & competence', url: 'http://localhost:8021' },
  { name: 'Validation Service', port: 8022, status: 'production', health: 'healthy', category: 'Operations', description: 'Exercises & audits', url: 'http://localhost:8022' },
  { name: 'Documents Service', port: 8024, status: 'development', health: 'degraded', category: 'Operations', description: 'Document management', url: 'http://localhost:8024' },
  { name: 'Plans Service', port: 8023, status: 'development', health: 'unknown', category: 'Operations', description: 'Plan repository', url: 'http://localhost:8023' },

  // Governance
  { name: 'Compliance Service', port: 8014, status: 'development', health: 'degraded', category: 'Governance', description: 'ISO 22301 compliance', url: 'http://localhost:8014' },
  { name: 'Governance Service', port: 8025, status: 'development', health: 'unknown', category: 'Governance', description: 'BCMS governance', url: 'http://localhost:8025' },

  // Intelligence
  { name: 'Digital Twin', port: 8096, status: 'production', health: 'healthy', category: 'Intelligence', description: 'System modeling & simulation', url: 'http://localhost:8096' },
  { name: 'AI Foundation', port: 8040, status: 'production', health: 'healthy', category: 'Intelligence', description: 'AI/ML services', url: 'http://localhost:8040' },
  { name: 'System BCM', port: 8050, status: 'production', health: 'healthy', category: 'Intelligence', description: 'Intelligent BCM orchestration', url: 'http://localhost:8050' },
  { name: 'Workflow Intelligence', port: 8037, status: 'production', health: 'healthy', category: 'Intelligence', description: 'Workflow optimization', url: 'http://localhost:8037' },
  { name: 'Community Service', port: 8030, status: 'production', health: 'healthy', category: 'Intelligence', description: 'Knowledge sharing', url: 'http://localhost:8030' },
  { name: 'Analytics Service', port: 8051, status: 'production', health: 'healthy', category: 'Intelligence', description: 'Platform analytics', url: 'http://localhost:8051' },
  { name: 'Simulation Service', port: 8095, status: 'production', health: 'healthy', category: 'Intelligence', description: 'Monte Carlo & simulations', url: 'http://localhost:8095' },
];

type TabType = 'topology' | 'clone' | 'simulations';

export default function DigitalTwinPage() {
  const [activeTab, setActiveTab] = useState<TabType>('topology');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Statistics
  const totalServices = platformServices.length;
  const activeServices = platformServices.filter(s => s.status === 'production').length;
  const healthyServices = platformServices.filter(s => s.health === 'healthy').length;
  const categories = Array.from(new Set(platformServices.map(s => s.category)));

  // Filter services
  const filteredServices = platformServices.filter(service => {
    const matchesSearch = service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         service.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || service.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getHealthIcon = (health: HealthStatus) => {
    switch (health) {
      case 'healthy': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'degraded': return <AlertCircle className="h-4 w-4 text-orange-600" />;
      case 'down': return <XCircle className="h-4 w-4 text-red-600" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: ServiceStatus) => {
    const styles = {
      production: 'bg-green-500/10 text-green-600 border-green-500/20',
      development: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
      disabled: 'bg-gray-500/10 text-gray-600 border-gray-500/20',
      unknown: 'bg-gray-500/10 text-gray-600 border-gray-500/20'
    };

    return (
      <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${styles[status]}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Digital Twin</h1>
        <p className="text-muted-foreground mt-2">
          Platform-wide service discovery, system modeling, and simulation
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex gap-6">
          <button
            onClick={() => setActiveTab('topology')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'topology'
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <div className="flex items-center gap-2">
              <Network className="h-4 w-4" />
              Platform Topology
            </div>
          </button>
          <button
            onClick={() => setActiveTab('clone')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'clone'
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <div className="flex items-center gap-2">
              <GitBranch className="h-4 w-4" />
              System Clone
            </div>
          </button>
          <button
            onClick={() => setActiveTab('simulations')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'simulations'
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <div className="flex items-center gap-2">
              <Play className="h-4 w-4" />
              Simulations
            </div>
          </button>
        </nav>
      </div>

      {/* Platform Topology Tab */}
      {activeTab === 'topology' && (
        <div className="space-y-6">
          {/* Overview Stats */}
          <div className="grid gap-4 md:grid-cols-4">
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-primary/10 p-3">
                  <Server className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Services</p>
                  <h3 className="text-2xl font-bold">{totalServices}</h3>
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-green-500/10 p-3">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Production</p>
                  <h3 className="text-2xl font-bold">{activeServices}</h3>
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-green-500/10 p-3">
                  <Activity className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Healthy</p>
                  <h3 className="text-2xl font-bold">{healthyServices}</h3>
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-blue-500/10 p-3">
                  <Database className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Categories</p>
                  <h3 className="text-2xl font-bold">{categories.length}</h3>
                </div>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-4 items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search services..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Categories</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>

            <button className="px-4 py-2 rounded-lg border hover:bg-accent transition-colors">
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>

          {/* Service Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredServices.map((service) => (
              <div key={service.port} className="rounded-lg border bg-card p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-primary/10 p-2">
                      <Zap className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm">{service.name}</h3>
                      <p className="text-xs text-muted-foreground">:{service.port}</p>
                    </div>
                  </div>
                  {getHealthIcon(service.health)}
                </div>

                <p className="text-sm text-muted-foreground mb-3">{service.description}</p>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusBadge(service.status)}
                    <span className="text-xs text-muted-foreground">{service.category}</span>
                  </div>
                  <button className="text-primary hover:underline text-sm flex items-center gap-1">
                    Details
                    <ChevronRight className="h-3 w-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {filteredServices.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              No services found matching your criteria
            </div>
          )}
        </div>
      )}

      {/* System Clone Tab */}
      {activeTab === 'clone' && (
        <div className="space-y-6">
          <div className="rounded-lg border bg-card p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-lg bg-blue-500/10 p-3">
                <Box className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-lg mb-2">System Clone</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Create digital mirrors of your platform for what-if analysis and safe testing
                </p>

                <div className="rounded-lg bg-muted/50 p-4 mb-4">
                  <h4 className="font-medium text-sm mb-2">What is System Clone?</h4>
                  <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                    <li>Create isolated copies of your entire platform state</li>
                    <li>Run simulations without affecting production</li>
                    <li>Test recovery procedures safely</li>
                    <li>Compare scenarios side-by-side</li>
                  </ul>
                </div>

                <button className="px-6 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium">
                  Create New Clone
                </button>
              </div>
            </div>
          </div>

          {/* Clone List Placeholder */}
          <div className="rounded-lg border bg-card p-8 text-center">
            <Box className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground mb-4">No system clones yet</p>
            <p className="text-sm text-muted-foreground">
              Create your first clone to start running simulations
            </p>
          </div>
        </div>
      )}

      {/* Simulations Tab */}
      {activeTab === 'simulations' && (
        <div className="space-y-6">
          <div className="rounded-lg border bg-card p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-lg bg-purple-500/10 p-3">
                <Play className="h-6 w-6 text-purple-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-lg mb-2">Simulation Hub</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Run Monte Carlo simulations, what-if scenarios, and impact analysis
                </p>

                <div className="grid gap-3 md:grid-cols-3 mb-4">
                  <div className="rounded-lg border bg-muted/50 p-3">
                    <p className="text-xs text-muted-foreground mb-1">Simulation Engines</p>
                    <p className="text-lg font-bold">7</p>
                    <p className="text-xs text-muted-foreground">Monte Carlo, Queue Theory, TOC...</p>
                  </div>
                  <div className="rounded-lg border bg-muted/50 p-3">
                    <p className="text-xs text-muted-foreground mb-1">Scenario Types</p>
                    <p className="text-lg font-bold">12+</p>
                    <p className="text-xs text-muted-foreground">Cyber, Disaster, Supply Chain...</p>
                  </div>
                  <div className="rounded-lg border bg-muted/50 p-3">
                    <p className="text-xs text-muted-foreground mb-1">Total Runs</p>
                    <p className="text-lg font-bold">0</p>
                    <p className="text-xs text-muted-foreground">No simulations yet</p>
                  </div>
                </div>

                <button className="px-6 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium">
                  Run New Simulation
                </button>
              </div>
            </div>
          </div>

          {/* Simulation Categories */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[
              { name: 'Monte Carlo', desc: 'Statistical uncertainty analysis', icon: '' },
              { name: 'Queue Theory', desc: 'Service capacity modeling', icon: '⏱️' },
              { name: 'TOC Analysis', desc: 'Theory of Constraints', icon: '' },
              { name: 'Impact Passport', desc: 'Cascading impact analysis', icon: '' },
              { name: 'Prediction', desc: 'Trend forecasting', icon: '' },
              { name: 'What-If', desc: 'Scenario exploration', icon: '' },
            ].map((engine) => (
              <div key={engine.name} className="rounded-lg border bg-card p-4 hover:shadow-md transition-shadow cursor-pointer">
                <div className="text-3xl mb-2">{engine.icon}</div>
                <h4 className="font-semibold mb-1">{engine.name}</h4>
                <p className="text-sm text-muted-foreground">{engine.desc}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Service Info Footer */}
      <div className="rounded-lg border bg-muted/50 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            <div className="text-sm">
              <span className="font-medium">Digital Twin Service</span>
              <span className="text-muted-foreground"> • Port 8096 • Production Ready</span>
            </div>
          </div>
          <div className="flex gap-2">
            <a
              href="http://localhost:8096/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline"
            >
              API Docs
            </a>
            <span className="text-muted-foreground">•</span>
            <a
              href="http://localhost:8096/health"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline"
            >
              Health Check
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
