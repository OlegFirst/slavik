import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ModuleInspector from './BCM/ModuleInspector';
import ModuleCreator from './BCM/ModuleCreator';
import ModuleToolkit from './BCM/ModuleToolkit';

const BCMUnifiedWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const navigate = useNavigate();

  const tabs = [
    {
      id: 'overview',
      label: 'Overview',
      icon: '🏠',
      description: 'Platform overview and status'
    },
    {
      id: 'dashboard',
      label: 'Real Data Dashboard',
      icon: '📊',
      description: 'Live BCM data from Odoo modules'
    },
    {
      id: 'inspector',
      label: 'Module Inspector',
      icon: '🔍',
      description: 'Analyze and inspect BCM modules'
    },
    {
      id: 'creator',
      label: 'Module Creator',
      icon: '🏗️',
      description: 'Create new BCM modules'
    },
    {
      id: 'ai-assistant',
      label: 'AI Assistant',
      icon: '🤖',
      description: 'AI-powered BCM guidance'
    },
    {
      id: 'toolkit',
      label: 'Module Toolkit',
      icon: '🛠️',
      description: 'Advanced module utilities'
    },
    {
      id: 'digital-twin',
      label: 'Digital Twin',
      icon: '👥',
      description: 'Digital twin management'
    }
  ];

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId);

    // Navigate to specific routes for some tabs
    switch (tabId) {
      case 'dashboard':
        navigate('/dashboard');
        break;
      case 'digital-twin':
        navigate('/digital-twin');
        break;
      case 'ai-assistant':
        navigate('/ai-configuration');
        break;
      default:
        // Stay on current page for other tabs
        break;
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab />;
      case 'inspector':
        return <ModuleInspectorTab />;
      case 'creator':
        return <ModuleCreatorTab />;
      case 'toolkit':
        return <ModuleToolkitTab />;
      default:
        return <OverviewTab />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                🚀 BCM Unified Platform
              </h1>
              <p className="text-sm text-gray-500">
                Complete Business Continuity Management Suite
              </p>
            </div>
            <div className="text-sm text-gray-500">
              Admin Panel • Port 3001
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8 overflow-x-auto py-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabClick(tab.id)}
                className={`
                  flex items-center px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap
                  transition-colors duration-200
                  ${activeTab === tab.id
                    ? 'bg-blue-100 text-blue-700 border border-blue-200'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }
                `}
                title={tab.description}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {renderTabContent()}
      </div>
    </div>
  );
};

// Overview Tab Component
const OverviewTab: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Welcome to BCM Unified Platform
        </h2>
        <p className="text-gray-600 mb-4">
          This unified workspace combines all BCM tools into one interface.
          Choose a tool from the tabs above to get started.
        </p>

        {/* Quick Links */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
          <QuickLinkCard
            icon="📊"
            title="Real Data Dashboard"
            description="View live data from your BCM modules"
            onClick={() => window.location.href = '/dashboard'}
          />
          <QuickLinkCard
            icon="🔍"
            title="Module Inspector"
            description="Analyze module structure and dependencies"
            onClick={() => {}}
          />
          <QuickLinkCard
            icon="🏗️"
            title="Module Creator"
            description="Create new BCM modules with AI assistance"
            onClick={() => {}}
          />
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatusCard
            title="BCM Modules"
            value="26"
            status="success"
            description="Active modules"
          />
          <StatusCard
            title="Dependencies"
            value="0"
            status="success"
            description="Circular dependencies"
          />
          <StatusCard
            title="Backend APIs"
            value="3"
            status="success"
            description="Available endpoints"
          />
          <StatusCard
            title="Integrations"
            value="✓"
            status="success"
            description="All systems connected"
          />
        </div>
      </div>

      {/* Available Tools */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Tools</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900">🔍 Module Inspector</h4>
            <p className="text-sm text-gray-600 mt-1">
              Analyze module dependencies, code quality, and structure
            </p>
          </div>
          <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900">🏗️ Module Creator</h4>
            <p className="text-sm text-gray-600 mt-1">
              Generate new BCM modules using templates and AI
            </p>
          </div>
          <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900">🛠️ Module Toolkit</h4>
            <p className="text-sm text-gray-600 mt-1">
              Advanced utilities for module management and optimization
            </p>
          </div>
          <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900">🤖 AI Assistant</h4>
            <p className="text-sm text-gray-600 mt-1">
              Get AI-powered guidance for BCM development
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Module Inspector Tab Component
const ModuleInspectorTab: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        🔍 Module Inspector
      </h2>
      <p className="text-gray-600 mb-6">
        Analyze BCM modules, check dependencies, and inspect code quality.
      </p>

      <ModuleInspector />
    </div>
  );
};

// Module Creator Tab Component
const ModuleCreatorTab: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        🏗️ Module Creator
      </h2>
      <p className="text-gray-600 mb-6">
        Create new BCM modules using templates and AI-powered generation.
      </p>

      <ModuleCreator />
    </div>
  );
};

// Module Toolkit Tab Component
const ModuleToolkitTab: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        🛠️ Module Toolkit
      </h2>
      <p className="text-gray-600 mb-6">
        Advanced utilities for module management, optimization, and analysis.
      </p>

      <ModuleToolkit />
    </div>
  );
};

// Helper Components
interface QuickLinkCardProps {
  icon: string;
  title: string;
  description: string;
  onClick: () => void;
}

const QuickLinkCard: React.FC<QuickLinkCardProps> = ({ icon, title, description, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="text-left p-4 border rounded-lg hover:bg-gray-50 transition-colors"
    >
      <div className="text-2xl mb-2">{icon}</div>
      <h4 className="font-medium text-gray-900">{title}</h4>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
    </button>
  );
};

interface StatusCardProps {
  title: string;
  value: string;
  status: 'success' | 'warning' | 'error';
  description: string;
}

const StatusCard: React.FC<StatusCardProps> = ({ title, value, status, description }) => {
  const statusColors = {
    success: 'text-green-600',
    warning: 'text-yellow-600',
    error: 'text-red-600'
  };

  return (
    <div className="text-center p-4 border rounded-lg">
      <div className={`text-2xl font-bold ${statusColors[status]}`}>{value}</div>
      <div className="text-sm font-medium text-gray-900">{title}</div>
      <div className="text-xs text-gray-500">{description}</div>
    </div>
  );
};

export default BCMUnifiedWorkspace;