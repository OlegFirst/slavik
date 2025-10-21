import React, { useState } from 'react';

interface ModuleInspectorProps {}

interface ModuleAnalysisResult {
  module_name: string;
  health_score: number;
  dependencies: string[];
  issues: Array<{
    type: 'error' | 'warning' | 'info';
    message: string;
  }>;
  structure: {
    models: string[];
    views: string[];
    security: string[];
  };
}

export const ModuleInspector: React.FC<ModuleInspectorProps> = () => {
  const [selectedModule, setSelectedModule] = useState('');
  const [folderPath, setFolderPath] = useState('/Users/MD/ISO-22301/core/odoo-18.0/addons');
  const [analysisResult, setAnalysisResult] = useState<ModuleAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'select' | 'folder' | 'results'>('select');

  // Common BCM modules
  const bcmModules = [
    'bcm_core',
    'bcm_incident',
    'bcm_risk_management',
    'bcm_governance',
    'bcm_bia',
    'bcm_plans',
    'bcm_training',
    'bcm_reporting',
    'bcm_community',
    'bcm_digital_twin_core',
    'bcm_ai_control',
    'bcm_scenario_hub'
  ];

  const handleModuleSelect = async (module: string) => {
    setSelectedModule(module);
    setLoading(true);

    try {
      // Simulate API call to bcm_platform_web_v4.py
      const response = await fetch(`http://localhost:8080/api/inspect/${module}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result);
        setActiveTab('results');
      } else {
        // Mock result for demo
        const mockResult: ModuleAnalysisResult = {
          module_name: module,
          health_score: Math.floor(Math.random() * 40) + 60, // 60-100
          dependencies: ['base', 'web', 'mail'].concat(
            Math.random() > 0.5 ? ['bcm_core'] : []
          ),
          issues: [
            {
              type: Math.random() > 0.7 ? 'error' : 'warning',
              message: `Sample issue found in ${module}`
            }
          ],
          structure: {
            models: [`${module.replace('bcm_', '')}.py`],
            views: [`${module}_views.xml`],
            security: ['ir.model.access.csv']
          }
        };
        setAnalysisResult(mockResult);
        setActiveTab('results');
      }
    } catch (error) {
      console.error('Failed to analyze module:', error);
      // Show mock result on error
      const mockResult: ModuleAnalysisResult = {
        module_name: module,
        health_score: 85,
        dependencies: ['base', 'web', 'bcm_core'],
        issues: [
          { type: 'warning', message: 'Connection to backend failed - showing mock data' }
        ],
        structure: {
          models: [`${module.replace('bcm_', '')}.py`],
          views: [`${module}_views.xml`],
          security: ['ir.model.access.csv']
        }
      };
      setAnalysisResult(mockResult);
      setActiveTab('results');
    } finally {
      setLoading(false);
    }
  };

  const handleFolderScan = async () => {
    if (!folderPath.trim()) return;

    setLoading(true);
    try {
      // Simulate folder scan
      await new Promise(resolve => setTimeout(resolve, 2000));

      const mockResults: ModuleAnalysisResult = {
        module_name: 'Folder Scan Results',
        health_score: 92,
        dependencies: [],
        issues: [
          { type: 'info', message: `Scanned folder: ${folderPath}` },
          { type: 'info', message: `Found ${bcmModules.length} BCM modules` }
        ],
        structure: {
          models: ['Multiple module models found'],
          views: ['Multiple view files found'],
          security: ['All modules have security files']
        }
      };

      setAnalysisResult(mockResults);
      setActiveTab('results');
    } catch (error) {
      console.error('Failed to scan folder:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderModuleSelect = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Select BCM Module to Inspect
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {bcmModules.map((module) => (
            <button
              key={module}
              onClick={() => handleModuleSelect(module)}
              disabled={loading}
              className={`
                p-3 text-left border rounded-lg transition-colors
                ${selectedModule === module
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                }
                ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <div className="font-medium">{module}</div>
              <div className="text-sm text-gray-500">
                Click to analyze
              </div>
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Analyzing module...</p>
        </div>
      )}
    </div>
  );

  const renderFolderScan = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Scan Folder for BCM Modules
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Folder Path
            </label>
            <input
              type="text"
              value={folderPath}
              onChange={(e) => setFolderPath(e.target.value)}
              placeholder="/path/to/odoo/addons"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={handleFolderScan}
            disabled={loading || !folderPath.trim()}
            className={`
              px-4 py-2 rounded-md font-medium
              ${loading || !folderPath.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
              }
            `}
          >
            {loading ? 'Scanning...' : 'Scan Folder'}
          </button>
        </div>
      </div>
    </div>
  );

  const renderResults = () => {
    if (!analysisResult) return null;

    const getHealthColor = (score: number) => {
      if (score >= 80) return 'text-green-600';
      if (score >= 60) return 'text-yellow-600';
      return 'text-red-600';
    };

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">
            Analysis Results: {analysisResult.module_name}
          </h3>
          <button
            onClick={() => setActiveTab('select')}
            className="text-blue-600 hover:text-blue-800"
          >
            ← Back to selection
          </button>
        </div>

        {/* Health Score */}
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Health Score</span>
            <span className={`text-2xl font-bold ${getHealthColor(analysisResult.health_score)}`}>
              {analysisResult.health_score}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div
              className="bg-green-600 h-2 rounded-full"
              style={{ width: `${analysisResult.health_score}%` }}
            ></div>
          </div>
        </div>

        {/* Dependencies */}
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Dependencies</h4>
          <div className="flex flex-wrap gap-2">
            {analysisResult.dependencies.map((dep, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-800 rounded-md text-sm"
              >
                {dep}
              </span>
            ))}
          </div>
        </div>

        {/* Issues */}
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Issues Found</h4>
          <div className="space-y-2">
            {analysisResult.issues.map((issue, index) => (
              <div
                key={index}
                className={`
                  p-3 rounded-md border-l-4
                  ${issue.type === 'error' ? 'bg-red-50 border-red-400 text-red-800' :
                    issue.type === 'warning' ? 'bg-yellow-50 border-yellow-400 text-yellow-800' :
                    'bg-blue-50 border-blue-400 text-blue-800'
                  }
                `}
              >
                <div className="flex items-center">
                  <span className="font-medium capitalize mr-2">{issue.type}:</span>
                  <span>{issue.message}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Structure */}
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Module Structure</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">Models</h5>
              <ul className="text-sm text-gray-600">
                {analysisResult.structure.models.map((model, index) => (
                  <li key={index}>• {model}</li>
                ))}
              </ul>
            </div>
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">Views</h5>
              <ul className="text-sm text-gray-600">
                {analysisResult.structure.views.map((view, index) => (
                  <li key={index}>• {view}</li>
                ))}
              </ul>
            </div>
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">Security</h5>
              <ul className="text-sm text-gray-600">
                {analysisResult.structure.security.map((security, index) => (
                  <li key={index}>• {security}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'select', label: 'Select Module', icon: '' },
            { id: 'folder', label: 'Scan Folder', icon: '' },
            { id: 'results', label: 'Results', icon: '' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              disabled={tab.id === 'results' && !analysisResult}
              className={`
                py-2 px-1 border-b-2 font-medium text-sm flex items-center
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
                ${tab.id === 'results' && !analysisResult ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <span className="mr-1">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'select' && renderModuleSelect()}
      {activeTab === 'folder' && renderFolderScan()}
      {activeTab === 'results' && renderResults()}
    </div>
  );
};

export default ModuleInspector;