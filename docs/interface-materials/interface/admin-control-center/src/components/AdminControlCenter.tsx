/**
 * AI Platform ISO 22301 - Admin Control Center
 * ============================================
 *
 * Full administrative portal with sidebar navigation
 * NO MOCK DATA - All real integrations
 */

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  LayoutDashboard,
  Server,
  Wrench,
  BarChart3,
  Eye,
  Settings,
  Users,
  Activity,
  Menu,
  X,
} from 'lucide-react';

// Import our components
import PlatformDashboard from './PlatformDashboard';
import ToolsManager from './ToolsManager';
import PrometheusMetrics from './PrometheusMetrics';
import GrafanaViewer from './GrafanaViewer';
import CentralizedArchitectureMonitor from './CentralizedArchitectureMonitor';
import SystemConfigManager from './SystemConfigManager';
import UserManager from './UserManager';

type MenuSection =
  | 'dashboard'
  | 'services'
  | 'tools'
  | 'metrics'
  | 'dashboards'
  | 'config'
  | 'users';

const MENU_ITEMS = [
  {
    id: 'dashboard' as MenuSection,
    label: 'Dashboard',
    icon: LayoutDashboard,
    description: 'Platform overview',
  },
  {
    id: 'services' as MenuSection,
    label: 'Services',
    icon: Server,
    description: 'Service health & architecture',
  },
  {
    id: 'tools' as MenuSection,
    label: 'Tools',
    icon: Wrench,
    description: 'Platform tools management',
  },
  {
    id: 'metrics' as MenuSection,
    label: 'Metrics',
    icon: BarChart3,
    description: 'Prometheus metrics',
  },
  {
    id: 'dashboards' as MenuSection,
    label: 'Dashboards',
    icon: Eye,
    description: 'Grafana visualization',
  },
  {
    id: 'config' as MenuSection,
    label: 'Configuration',
    icon: Settings,
    description: 'System settings',
  },
  {
    id: 'users' as MenuSection,
    label: 'Users',
    icon: Users,
    description: 'User management',
  },
];

export const AdminControlCenter: React.FC = () => {
  const [activeSection, setActiveSection] = useState<MenuSection>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <PlatformDashboard />;
      case 'services':
        return <CentralizedArchitectureMonitor />;
      case 'tools':
        return <ToolsManager />;
      case 'metrics':
        return <PrometheusMetrics />;
      case 'dashboards':
        return <GrafanaViewer />;
      case 'config':
        return <SystemConfigManager />;
      case 'users':
        return <UserManager />;
      default:
        return <PlatformDashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-0'
        } bg-gradient-to-br from-gray-900 to-gray-800 text-white transition-all duration-300 overflow-hidden flex flex-col`}
      >
        {/* Sidebar Header */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold">AI Platform</h1>
              <p className="text-xs text-gray-400">ISO 22301</p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-white hover:bg-gray-700"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-2">
          {MENU_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;

            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                <div className="flex-1 text-left">
                  <div className="font-medium text-sm">{item.label}</div>
                  <div className="text-xs opacity-75">{item.description}</div>
                </div>
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <Activity className="w-4 h-4 text-green-500" />
            <span>System Online</span>
          </div>
          <div className="text-xs text-gray-500 mt-2">
            Version 2.0.0
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {!sidebarOpen && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSidebarOpen(true)}
                >
                  <Menu className="w-4 h-4" />
                </Button>
              )}
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {MENU_ITEMS.find((item) => item.id === activeSection)?.label}
                </h2>
                <p className="text-sm text-gray-600">
                  {MENU_ITEMS.find((item) => item.id === activeSection)?.description}
                </p>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-gray-500">Last Updated</div>
                <div className="text-sm font-medium">{new Date().toLocaleTimeString()}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-auto">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default AdminControlCenter;
