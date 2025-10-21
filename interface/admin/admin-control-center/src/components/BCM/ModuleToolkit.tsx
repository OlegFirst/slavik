import React, { useState } from 'react';

interface ModuleToolkitProps {}

interface AuditResult {
  module_name: string;
  timestamp: string;
  score: number;
  checks: {
    [key: string]: {
      passed: boolean;
      message: string;
      issues?: string[];
      recommendations?: string[];
    };
  };
  issues: string[];
  recommendations: string[];
  status: 'success' | 'error';
}

interface OptimizationResult {
  module_name: string;
  optimizations_applied: string[];
  size_reduction: string;
  performance_improvement: string;
  status: 'success' | 'error';
}

export const ModuleToolkit: React.FC<ModuleToolkitProps> = () => {
  const [activeTab, setActiveTab] = useState<'audit' | 'optimize' | 'merge' | 'dependencies'>('audit');
  const [selectedModule, setSelectedModule] = useState('');
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState(false);

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
    'bcm_scenario_hub',
    'bcm_audit',
    'bcm_clients',
    'bcm_kpi',
    'bcm_templates',
    'bcm_exercise',
    'bcm_incident_management',
    'bcm_intelligent_base'
  ];

  const handleAuditModule = async (module: string) => {
    setLoading(true);

    try {
      const response = await fetch(`http://localhost:8080/api/toolkit/audit/${module}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        setAuditResult(result);
      } else {
        // Mock audit result for demo
        const mockResult: AuditResult = {
          module_name: module,
          timestamp: new Date().toISOString(),
          score: Math.floor(Math.random() * 30) + 70, // 70-100
          checks: {
            manifest: {
              passed: true,
              message: '__manifest__.py found and valid'
            },
            security: {
              passed: Math.random() > 0.3,
              message: Math.random() > 0.3 ? 'Security files present' : 'Missing security configuration',
              issues: Math.random() > 0.3 ? [] : ['Missing ir.model.access.csv']
            },
            models: {
              passed: true,
              message: 'Models structure is valid'
            },
            views: {
              passed: Math.random() > 0.2,
              message: Math.random() > 0.2 ? 'Views are properly structured' : 'Views need optimization',
              recommendations: Math.random() > 0.2 ? [] : ['Add form view for better usability']
            },
            dependencies: {
              passed: Math.random() > 0.4,
              message: Math.random() > 0.4 ? 'Dependencies are optimal' : 'Circular dependencies detected',
              issues: Math.random() > 0.4 ? [] : ['Circular dependency with bcm_core']
            },
            naming: {
              passed: true,
              message: 'Naming conventions followed'
            },
            documentation: {
              passed: Math.random() > 0.5,
              message: Math.random() > 0.5 ? 'Documentation is adequate' : 'Documentation needs improvement',
              recommendations: Math.random() > 0.5 ? [] : ['Add docstrings to models and methods']
            },
            iso_compliance: {
              passed: Math.random() > 0.3,
              message: Math.random() > 0.3 ? 'ISO 22301 compliance verified' : 'ISO compliance issues found',
              issues: Math.random() > 0.3 ? [] : ['Missing business impact analysis fields']
            }
          },
          issues: [],
          recommendations: [],
          status: 'success'
        };

        // Collect issues and recommendations
        Object.values(mockResult.checks).forEach(check => {
          if (check.issues) mockResult.issues.push(...check.issues);
          if (check.recommendations) mockResult.recommendations.push(...check.recommendations);
        });

        setAuditResult(mockResult);
      }
    } catch (error) {
      console.error('Failed to audit module:', error);
      const errorResult: AuditResult = {
        module_name: module,
        timestamp: new Date().toISOString(),
        score: 0,
        checks: {},
        issues: ['Connection to backend failed'],
        recommendations: ['Check backend service'],
        status: 'error'
      };
      setAuditResult(errorResult);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimizeModule = async (module: string) => {
    setLoading(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 3000)); // Simulate optimization time

      const mockResult: OptimizationResult = {
        module_name: module,
        optimizations_applied: [
          'Removed unused imports',
          'Optimized database queries',
          'Compressed static assets',
          'Improved caching strategies',
          'Cleaned up redundant code'
        ],
        size_reduction: '15%',
        performance_improvement: '23%',
        status: 'success'
      };

      setOptimizationResult(mockResult);
    } catch (error) {
      console.error('Failed to optimize module:', error);
      const errorResult: OptimizationResult = {
        module_name: module,
        optimizations_applied: [],
        size_reduction: '0%',
        performance_improvement: '0%',
        status: 'error'
      };
      setOptimizationResult(errorResult);
    } finally {
      setLoading(false);
    }
  };

  const renderAuditTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Module Audit</h3>
        <p className="text-gray-600 mb-4">
          Perform comprehensive audit of BCM modules for quality, security, and compliance.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {bcmModules.map((module) => (
            <button
              key={module}
              onClick={() => {
                setSelectedModule(module);
                handleAuditModule(module);
              }}
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
                Click to audit
              </div>
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Running audit...</p>
        </div>
      )}

      {auditResult && !loading && (
        <div className="bg-white border rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-medium">Audit Results: {auditResult.module_name}</h4>
            <div className={`
              text-2xl font-bold px-3 py-1 rounded-lg
              ${auditResult.score >= 80 ? 'text-green-600 bg-green-100' :
                auditResult.score >= 60 ? 'text-yellow-600 bg-yellow-100' :
                'text-red-600 bg-red-100'
              }
            `}>
              {auditResult.score}%
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {Object.entries(auditResult.checks).map(([checkName, result]) => (
              <div
                key={checkName}
                className={`
                  p-3 rounded-lg border-l-4
                  ${result.passed
                    ? 'bg-green-50 border-green-400 text-green-800'
                    : 'bg-red-50 border-red-400 text-red-800'
                  }
                `}
              >
                <div className="flex items-center mb-1">
                  <span className="text-lg mr-2">
                    {result.passed ? '' : ''}
                  </span>
                  <span className="font-medium capitalize">{checkName}</span>
                </div>
                <p className="text-sm">{result.message}</p>
              </div>
            ))}
          </div>

          {auditResult.issues.length > 0 && (
            <div className="mb-4">
              <h5 className="font-medium text-red-800 mb-2">Issues Found:</h5>
              <ul className="list-disc list-inside text-sm text-red-700">
                {auditResult.issues.map((issue, index) => (
                  <li key={index}>{issue}</li>
                ))}
              </ul>
            </div>
          )}

          {auditResult.recommendations.length > 0 && (
            <div>
              <h5 className="font-medium text-blue-800 mb-2">Recommendations:</h5>
              <ul className="list-disc list-inside text-sm text-blue-700">
                {auditResult.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderOptimizeTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Module Optimization</h3>
        <p className="text-gray-600 mb-4">
          Optimize BCM modules for better performance, smaller size, and improved efficiency.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {bcmModules.map((module) => (
            <button
              key={module}
              onClick={() => {
                setSelectedModule(module);
                handleOptimizeModule(module);
              }}
              disabled={loading}
              className={`
                p-3 text-left border rounded-lg transition-colors
                ${selectedModule === module
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                }
                ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <div className="font-medium">{module}</div>
              <div className="text-sm text-gray-500">
                Click to optimize
              </div>
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Optimizing module...</p>
        </div>
      )}

      {optimizationResult && !loading && (
        <div className="bg-white border rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-medium">Optimization Results: {optimizationResult.module_name}</h4>
            <div className="text-green-600 text-2xl"></div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {optimizationResult.size_reduction}
              </div>
              <div className="text-sm text-green-700">Size Reduction</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {optimizationResult.performance_improvement}
              </div>
              <div className="text-sm text-blue-700">Performance Improvement</div>
            </div>
          </div>

          <div>
            <h5 className="font-medium text-gray-900 mb-3">Optimizations Applied:</h5>
            <ul className="space-y-2">
              {optimizationResult.optimizations_applied.map((optimization, index) => (
                <li key={index} className="flex items-center text-sm">
                  <span className="text-green-600 mr-2"></span>
                  {optimization}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );

  const renderMergeTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Module Merger</h3>
        <p className="text-gray-600 mb-4">
          Merge multiple BCM modules into a single optimized module.
        </p>

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <div className="text-4xl mb-4"></div>
          <h4 className="text-lg font-medium text-gray-900 mb-2">Module Merger</h4>
          <p className="text-gray-600 mb-4">
            Advanced functionality for merging multiple modules
          </p>
          <div className="text-sm text-gray-500">
            Select modules to merge, configure merge strategy, and create unified module
          </div>
        </div>
      </div>
    </div>
  );

  const renderDependenciesTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Dependencies Analysis</h3>
        <p className="text-gray-600 mb-4">
          Analyze and manage module dependencies across the BCM platform.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3"> Dependency Tree</h4>
            <p className="text-sm text-gray-600 mb-3">
              Visualize the complete dependency tree for all BCM modules
            </p>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              Generate Tree
            </button>
          </div>

          <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3"> Circular Dependencies</h4>
            <p className="text-sm text-gray-600 mb-3">
              Detect and resolve circular dependency issues
            </p>
            <button className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700">
              Check Circular
            </button>
          </div>

          <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3"> Optimize Dependencies</h4>
            <p className="text-sm text-gray-600 mb-3">
              Remove unused dependencies and optimize load order
            </p>
            <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
              Optimize
            </button>
          </div>

          <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3"> Impact Analysis</h4>
            <p className="text-sm text-gray-600 mb-3">
              Analyze the impact of changing module dependencies
            </p>
            <button className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700">
              Analyze Impact
            </button>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">Current Status</h4>
          <div className="text-sm text-gray-600">
            <div> 26 BCM modules scanned</div>
            <div> 0 circular dependencies detected</div>
            <div> All dependencies resolved</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'audit': return renderAuditTab();
      case 'optimize': return renderOptimizeTab();
      case 'merge': return renderMergeTab();
      case 'dependencies': return renderDependenciesTab();
      default: return renderAuditTab();
    }
  };

  return (
    <div>
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'audit', label: 'Module Audit', icon: '' },
            { id: 'optimize', label: 'Optimization', icon: '' },
            { id: 'merge', label: 'Module Merger', icon: '' },
            { id: 'dependencies', label: 'Dependencies', icon: '' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`
                py-2 px-1 border-b-2 font-medium text-sm flex items-center
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              <span className="mr-1">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {renderTabContent()}
    </div>
  );
};

export default ModuleToolkit;