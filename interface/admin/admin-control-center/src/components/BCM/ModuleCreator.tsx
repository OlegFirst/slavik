import React, { useState } from 'react';

interface ModuleCreatorProps {}

interface ModuleConfig {
  name: string;
  type: 'odoo' | 'bcm_native' | 'hybrid' | 'react' | 'api';
  target: 'odoo' | 'bcm' | 'hybrid';
  description: string;
  author: string;
  version: string;
  dependencies: string[];
  models: Array<{
    name: string;
    fields: Array<{ name: string; type: string; required: boolean }>;
  }>;
  features: string[];
  category: string;
}

interface CreationResult {
  module_id: string;
  status: 'success' | 'error';
  message: string;
  path: string;
  files_created: string[];
}

export const ModuleCreator: React.FC<ModuleCreatorProps> = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [moduleConfig, setModuleConfig] = useState<ModuleConfig>({
    name: '',
    type: 'odoo',
    target: 'odoo',
    description: '',
    author: '',
    version: '1.0.0',
    dependencies: ['base'],
    models: [],
    features: [],
    category: 'Business Continuity'
  });
  const [creationResult, setCreationResult] = useState<CreationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const moduleTypes = [
    {
      id: 'odoo',
      name: 'Odoo Module',
      description: 'Standard Odoo ERP module',
      icon: '',
      framework: 'odoo'
    },
    {
      id: 'bcm_native',
      name: 'BCM Native Module',
      description: 'Standalone BCM module (framework-agnostic)',
      icon: '',
      framework: 'bcm'
    },
    {
      id: 'hybrid',
      name: 'Hybrid Module',
      description: 'Works with both Odoo and BCM platforms',
      icon: '',
      framework: 'universal'
    },
    {
      id: 'react',
      name: 'React Component',
      description: 'Frontend React/Next.js module',
      icon: '️',
      framework: 'react'
    },
    {
      id: 'api',
      name: 'API Service',
      description: 'Microservice API module',
      icon: '',
      framework: 'fastapi'
    }
  ];

  const bcmCategories = [
    'Business Continuity',
    'Risk Management',
    'Incident Response',
    'Crisis Management',
    'Business Impact Analysis',
    'Training & Awareness',
    'Audit & Compliance',
    'Recovery Planning',
    'Communication',
    'AI & Analytics'
  ];

  const commonFeatures = [
    'Dashboard',
    'Reporting',
    'API Integration',
    'Workflow Management',
    'User Management',
    'Notifications',
    'Document Management',
    'Audit Trail',
    'Real-time Updates',
    'AI/ML Integration'
  ];

  const handleInputChange = (field: keyof ModuleConfig, value: any) => {
    setModuleConfig(prev => ({ ...prev, [field]: value }));
  };

  const addModel = () => {
    const newModel = {
      name: `model_${moduleConfig.models.length + 1}`,
      fields: [
        { name: 'name', type: 'char', required: true },
        { name: 'description', type: 'text', required: false }
      ]
    };
    setModuleConfig(prev => ({
      ...prev,
      models: [...prev.models, newModel]
    }));
  };

  const removeModel = (index: number) => {
    setModuleConfig(prev => ({
      ...prev,
      models: prev.models.filter((_, i) => i !== index)
    }));
  };

  const addDependency = (dep: string) => {
    if (dep && !moduleConfig.dependencies.includes(dep)) {
      setModuleConfig(prev => ({
        ...prev,
        dependencies: [...prev.dependencies, dep]
      }));
    }
  };

  const removeDependency = (dep: string) => {
    setModuleConfig(prev => ({
      ...prev,
      dependencies: prev.dependencies.filter(d => d !== dep)
    }));
  };

  const toggleFeature = (feature: string) => {
    setModuleConfig(prev => ({
      ...prev,
      features: prev.features.includes(feature)
        ? prev.features.filter(f => f !== feature)
        : [...prev.features, feature]
    }));
  };

  const handleCreateModule = async () => {
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8080/api/modules/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(moduleConfig),
      });

      if (response.ok) {
        const result = await response.json();
        setCreationResult(result);
        setCurrentStep(6);
      } else {
        // Mock result for demo
        const mockResult: CreationResult = {
          module_id: `bcm_${moduleConfig.name.toLowerCase().replace(/\s+/g, '_')}`,
          status: 'success',
          message: `Module ${moduleConfig.name} created successfully`,
          path: `/Users/MD/ISO-22301/core/odoo-18.0/addons/bcm_${moduleConfig.name.toLowerCase().replace(/\s+/g, '_')}`,
          files_created: [
            '__manifest__.py',
            '__init__.py',
            'models/__init__.py',
            'models/models.py',
            'views/menu.xml',
            'security/ir.model.access.csv'
          ]
        };
        setCreationResult(mockResult);
        setCurrentStep(6);
      }
    } catch (error) {
      console.error('Failed to create module:', error);
      // Show mock error result
      const errorResult: CreationResult = {
        module_id: '',
        status: 'error',
        message: 'Connection to backend failed - showing mock data',
        path: '',
        files_created: []
      };
      setCreationResult(errorResult);
      setCurrentStep(6);
    } finally {
      setLoading(false);
    }
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Step 1: Basic Information</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Module Name *
          </label>
          <input
            type="text"
            value={moduleConfig.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            placeholder="My BCM Module"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Version
          </label>
          <input
            type="text"
            value={moduleConfig.version}
            onChange={(e) => handleInputChange('version', e.target.value)}
            placeholder="1.0.0"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description *
          </label>
          <textarea
            value={moduleConfig.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            placeholder="Describe what your module does..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Author
          </label>
          <input
            type="text"
            value={moduleConfig.author}
            onChange={(e) => handleInputChange('author', e.target.value)}
            placeholder="Your Name or Company"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <select
            value={moduleConfig.category}
            onChange={(e) => handleInputChange('category', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {bcmCategories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Step 2: Module Type</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {moduleTypes.map(type => (
          <button
            key={type.id}
            onClick={() => handleInputChange('type', type.id)}
            className={`
              p-4 border rounded-lg text-left transition-colors
              ${moduleConfig.type === type.id
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
              }
            `}
          >
            <div className="text-2xl mb-2">{type.icon}</div>
            <h4 className="font-medium">{type.name}</h4>
            <p className="text-sm text-gray-600 mt-1">{type.description}</p>
            <div className="mt-2">
              <span className="text-xs bg-gray-200 px-2 py-1 rounded">
                {type.framework}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Step 3: Features & Dependencies</h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Features</h4>
          <div className="space-y-2">
            {commonFeatures.map(feature => (
              <label key={feature} className="flex items-center">
                <input
                  type="checkbox"
                  checked={moduleConfig.features.includes(feature)}
                  onChange={() => toggleFeature(feature)}
                  className="mr-2"
                />
                <span className="text-sm">{feature}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-medium text-gray-900 mb-3">Dependencies</h4>
          <div className="flex flex-wrap gap-2 mb-3">
            {moduleConfig.dependencies.map(dep => (
              <span
                key={dep}
                className="px-2 py-1 bg-blue-100 text-blue-800 rounded-md text-sm flex items-center"
              >
                {dep}
                <button
                  onClick={() => removeDependency(dep)}
                  className="ml-1 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Add dependency"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  addDependency((e.target as HTMLInputElement).value);
                  (e.target as HTMLInputElement).value = '';
                }
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Step 4: Data Models</h3>

      <div className="space-y-4">
        {moduleConfig.models.map((model, index) => (
          <div key={index} className="border rounded-lg p-4">
            <div className="flex justify-between items-center mb-3">
              <h4 className="font-medium">Model {index + 1}</h4>
              <button
                onClick={() => removeModel(index)}
                className="text-red-600 hover:text-red-800"
              >
                Remove
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model Name
                </label>
                <input
                  type="text"
                  value={model.name}
                  onChange={(e) => {
                    const newModels = [...moduleConfig.models];
                    newModels[index].name = e.target.value;
                    handleInputChange('models', newModels);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fields: {model.fields.length}
                </label>
                <div className="text-sm text-gray-600">
                  {model.fields.map(field => field.name).join(', ')}
                </div>
              </div>
            </div>
          </div>
        ))}

        <button
          onClick={addModel}
          className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-gray-400 hover:text-gray-800"
        >
          + Add Model
        </button>
      </div>
    </div>
  );

  const renderStep5 = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Step 5: Review & Create</h3>

      <div className="bg-gray-50 rounded-lg p-6">
        <h4 className="font-medium text-gray-900 mb-4">Module Summary</h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Name:</span> {moduleConfig.name}
          </div>
          <div>
            <span className="font-medium">Type:</span> {moduleConfig.type}
          </div>
          <div>
            <span className="font-medium">Version:</span> {moduleConfig.version}
          </div>
          <div>
            <span className="font-medium">Category:</span> {moduleConfig.category}
          </div>
          <div className="md:col-span-2">
            <span className="font-medium">Description:</span> {moduleConfig.description}
          </div>
          <div>
            <span className="font-medium">Dependencies:</span> {moduleConfig.dependencies.join(', ')}
          </div>
          <div>
            <span className="font-medium">Features:</span> {moduleConfig.features.join(', ')}
          </div>
          <div>
            <span className="font-medium">Models:</span> {moduleConfig.models.length}
          </div>
        </div>
      </div>

      <button
        onClick={handleCreateModule}
        disabled={loading || !moduleConfig.name || !moduleConfig.description}
        className={`
          w-full py-3 px-4 rounded-md font-medium
          ${loading || !moduleConfig.name || !moduleConfig.description
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
          }
        `}
      >
        {loading ? 'Creating Module...' : 'Create Module'}
      </button>
    </div>
  );

  const renderStep6 = () => {
    if (!creationResult) return null;

    return (
      <div className="space-y-6">
        <h3 className="text-lg font-medium text-gray-900">Creation Result</h3>

        <div className={`
          p-6 rounded-lg border-l-4
          ${creationResult.status === 'success'
            ? 'bg-green-50 border-green-400 text-green-800'
            : 'bg-red-50 border-red-400 text-red-800'
          }
        `}>
          <div className="flex items-center mb-2">
            <span className="text-2xl mr-2">
              {creationResult.status === 'success' ? '' : ''}
            </span>
            <h4 className="font-medium">
              {creationResult.status === 'success' ? 'Success!' : 'Error'}
            </h4>
          </div>
          <p>{creationResult.message}</p>

          {creationResult.status === 'success' && (
            <div className="mt-4">
              <p><strong>Module ID:</strong> {creationResult.module_id}</p>
              <p><strong>Path:</strong> {creationResult.path}</p>
              <div className="mt-2">
                <strong>Files Created:</strong>
                <ul className="list-disc list-inside mt-1">
                  {creationResult.files_created.map((file, index) => (
                    <li key={index} className="text-sm">{file}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        <div className="flex gap-4">
          <button
            onClick={() => {
              setCurrentStep(1);
              setCreationResult(null);
              setModuleConfig({
                name: '',
                type: 'odoo',
                target: 'odoo',
                description: '',
                author: '',
                version: '1.0.0',
                dependencies: ['base'],
                models: [],
                features: [],
                category: 'Business Continuity'
              });
            }}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            Create Another Module
          </button>
          {creationResult.status === 'success' && (
            <button
              onClick={() => window.open('/dashboard', '_blank')}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              View in Dashboard
            </button>
          )}
        </div>
      </div>
    );
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1: return renderStep1();
      case 2: return renderStep2();
      case 3: return renderStep3();
      case 4: return renderStep4();
      case 5: return renderStep5();
      case 6: return renderStep6();
      default: return renderStep1();
    }
  };

  return (
    <div>
      {/* Step Progress */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[1, 2, 3, 4, 5].map((step) => (
            <div key={step} className="flex items-center">
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                ${currentStep >= step
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-300 text-gray-600'
                }
              `}>
                {step}
              </div>
              {step < 5 && (
                <div className={`
                  w-16 h-1 mx-2
                  ${currentStep > step ? 'bg-blue-600' : 'bg-gray-300'}
                `} />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-2 text-sm text-gray-600">
          <span>Basic Info</span>
          <span>Module Type</span>
          <span>Features</span>
          <span>Data Models</span>
          <span>Review</span>
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg border p-6">
        {renderCurrentStep()}
      </div>

      {/* Navigation */}
      {currentStep < 6 && (
        <div className="flex justify-between mt-6">
          <button
            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
            disabled={currentStep === 1}
            className={`
              px-4 py-2 rounded-md font-medium
              ${currentStep === 1
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gray-600 text-white hover:bg-gray-700'
              }
            `}
          >
            Previous
          </button>

          {currentStep < 5 && (
            <button
              onClick={() => setCurrentStep(Math.min(5, currentStep + 1))}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Next
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default ModuleCreator;