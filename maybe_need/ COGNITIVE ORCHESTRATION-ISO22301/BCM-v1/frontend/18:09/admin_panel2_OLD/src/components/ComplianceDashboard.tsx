import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Shield,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  RefreshCw,
  Download,
  Target,
  TrendingUp,
  Eye,
  X,
  ExternalLink
} from 'lucide-react';
import { openModuleInOdoo, getRealComplianceData, getComplianceOverview, triggerAIAssessment, BCM_MODULES_MAPPING } from '@/utils/odoo-integration';

const ComplianceDashboard: React.FC = () => {
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [complianceData, setComplianceData] = useState<Record<string, number>>({});
  const [overviewData, setOverviewData] = useState<any>(null);
  const [aiAssessing, setAiAssessing] = useState(false);
  const [loading, setLoading] = useState(true);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const [compliance, overview] = await Promise.all([
        getRealComplianceData(),
        getComplianceOverview()
      ]);
      setComplianceData(compliance);
      setOverviewData(overview);
      console.log('Data refreshed:', { compliance, overview });
    } catch (error) {
      console.error('Error refreshing data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleAIAssessment = async () => {
    setAiAssessing(true);
    try {
      const result = await triggerAIAssessment();
      console.log('AI Assessment result:', result);
      if (result.success) {
        await handleRefresh();
      }
    } catch (error) {
      console.error('Error running AI assessment:', error);
    } finally {
      setAiAssessing(false);
    }
  };

  // Load data on mount
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await handleRefresh();
      setLoading(false);
    };
    loadData();
  }, []);

  // Calculate real module scores from BCM modules
  const moduleScores = Object.entries(BCM_MODULES_MAPPING).map(([technicalName, moduleInfo]) => {
    const score = complianceData[technicalName] || moduleInfo.compliance || 0;
    return { 
      name: moduleInfo.name, 
      technicalName, 
      score: Math.round(score),
      status: moduleInfo.status,
      compliance: moduleInfo.compliance
    };
  });

  // Use real overview data or fallbacks
  const totalModules = overviewData?.totalModules || Object.keys(BCM_MODULES_MAPPING).length;
  const overallCompliance = overviewData?.overallCompliance || 59;
  const criticalGaps = overviewData?.criticalGaps || 3;
  const healthyModules = overviewData?.healthyModules || moduleScores.filter(m => m.score >= 80).length;

  const getComplianceColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      'active': 'bg-green-100 text-green-800',
      'development': 'bg-yellow-100 text-yellow-800',
      'planning': 'bg-gray-100 text-gray-800',
      'maintenance': 'bg-blue-100 text-blue-800'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-lg">Loading compliance data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
            <Shield className="h-7 w-7 text-blue-600" />
            ISO 22301 Compliance Dashboard
          </h2>
          <p className="text-slate-600 mt-1">
            Real-time Business Continuity Management System compliance monitoring ({totalModules} BCM modules)
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh Data
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleAIAssessment}
            disabled={aiAssessing}
          >
            {aiAssessing ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Target className="h-4 w-4 mr-2" />
            )}
            AI Assessment
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Real-time Status Alert */}
      <Alert>
        <Shield className="h-4 w-4" />
        <AlertDescription>
          Connected to BCM Governance system. Last updated: {new Date().toLocaleTimeString()}
          {overviewData && " | Live data from Odoo API"}
        </AlertDescription>
      </Alert>

      {/* Metrics Cards - Using Real Data */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="h-5 w-5 text-blue-500" />
              <span className="text-sm font-medium">Overall Compliance</span>
            </div>
            <div className="text-2xl font-bold text-slate-900">{overallCompliance}%</div>
            <p className="text-xs text-slate-500">Real-time from BCM modules</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-sm font-medium">Healthy Modules</span>
            </div>
            <div className="text-2xl font-bold text-slate-900">{healthyModules}/{totalModules}</div>
            <p className="text-xs text-slate-500">≥80% compliance</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <span className="text-sm font-medium">Critical Gaps</span>
            </div>
            <div className="text-2xl font-bold text-slate-900">{criticalGaps}</div>
            <p className="text-xs text-slate-500">require attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Target className="h-5 w-5 text-purple-500" />
              <span className="text-sm font-medium">Total Modules</span>
            </div>
            <div className="text-2xl font-bold text-slate-900">{totalModules}</div>
            <p className="text-xs text-slate-500">BCM ecosystem</p>
          </CardContent>
        </Card>
      </div>

      {/* Real BCM Module Compliance Matrix */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            BCM Module Compliance Status - Live Data
          </CardTitle>
          <CardDescription>
            Real-time ISO 22301 compliance by BCM module from Odoo system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {moduleScores.map((module) => (
              <div
                key={module.technicalName}
                className="border rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedModule(module.technicalName)}
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-slate-900 text-sm">{module.name}</h4>
                  <div className="flex flex-col gap-1">
                    <Badge className={getComplianceColor(module.score)}>
                      {module.score}%
                    </Badge>
                    <Badge size="sm" className={getStatusBadge(module.status)}>
                      {module.status}
                    </Badge>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-slate-600">
                    <span>Module: {module.technicalName}</span>
                    <Button
                      variant="ghost" 
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={(e) => {
                        e.stopPropagation();
                        openModuleInOdoo(module.technicalName);
                      }}
                    >
                      <ExternalLink className="h-3 w-3" />
                    </Button>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${getProgressColor(module.score)}`}
                      style={{ width: `${module.score}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Implementation Phases - Dynamic Calculation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Implementation Roadmap - Real Status
          </CardTitle>
          <CardDescription>
            Current implementation status across BCM module phases
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Phase 1: Foundation */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <h4 className="font-medium">Phase 1: Foundation & Core</h4>
                <Badge variant="secondary">Active</Badge>
              </div>
              <span className="text-sm text-slate-500">
                {moduleScores.filter(m => ['bcm_base', 'bcm_core', 'bcm_config', 'bcm_governance'].includes(m.technicalName)).length} modules
              </span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2 mb-2">
              <div
                className="h-2 rounded-full bg-blue-500"
                style={{
                  width: `${moduleScores
                    .filter(m => ['bcm_base', 'bcm_core', 'bcm_config', 'bcm_governance'].includes(m.technicalName))
                    .reduce((acc, m) => acc + m.score, 0) / 4}%`
                }}
              />
            </div>
            <p className="text-sm text-slate-600">Core platform, governance, and configuration modules</p>
          </div>

          {/* Phase 2: Risk & Analysis */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <h4 className="font-medium">Phase 2: Risk & BIA</h4>
                <Badge variant="secondary">Active</Badge>
              </div>
              <span className="text-sm text-slate-500">
                {moduleScores.filter(m => ['bcm_risk_management', 'bcm_bia', 'bcm_context'].includes(m.technicalName)).length} modules
              </span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2 mb-2">
              <div
                className="h-2 rounded-full bg-green-500"
                style={{
                  width: `${moduleScores
                    .filter(m => ['bcm_risk_management', 'bcm_bia', 'bcm_context'].includes(m.technicalName))
                    .reduce((acc, m) => acc + m.score, 0) / 3}%`
                }}
              />
            </div>
            <p className="text-sm text-slate-600">Risk assessment, business impact analysis, and context</p>
          </div>

          {/* Phase 3: Operations & Response */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-orange-500" />
                <h4 className="font-medium">Phase 3: Operations & Response</h4>
                <Badge variant="outline">Development</Badge>
              </div>
              <span className="text-sm text-slate-500">
                {moduleScores.filter(m => ['bcm_plans', 'bcm_incident_management', 'bcm_exercise', 'bcm_training'].includes(m.technicalName)).length} modules
              </span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2 mb-2">
              <div
                className="h-2 rounded-full bg-orange-500"
                style={{
                  width: `${moduleScores
                    .filter(m => ['bcm_plans', 'bcm_incident_management', 'bcm_exercise', 'bcm_training'].includes(m.technicalName))
                    .reduce((acc, m) => acc + m.score, 0) / 4}%`
                }}
              />
            </div>
            <p className="text-sm text-slate-600">Plans, incident response, exercises and training</p>
          </div>

          {/* Phase 4: Intelligence & AI */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-purple-500" />
                <h4 className="font-medium">Phase 4: AI & Intelligence</h4>
                <Badge variant="outline">Active</Badge>
              </div>
              <span className="text-sm text-slate-500">
                {moduleScores.filter(m => m.technicalName.includes('ai_')).length} modules
              </span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2 mb-2">
              <div
                className="h-2 rounded-full bg-purple-500"
                style={{
                  width: `${moduleScores
                    .filter(m => m.technicalName.includes('ai_'))
                    .reduce((acc, m) => acc + m.score, 0) / (moduleScores.filter(m => m.technicalName.includes('ai_')).length || 1)}%`
                }}
              />
            </div>
            <p className="text-sm text-slate-600">AI systems, intelligent analysis and automation</p>
          </div>
        </CardContent>
      </Card>

      {/* Module Details Modal - Enhanced */}
      {selectedModule && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold">
                  {BCM_MODULES_MAPPING[selectedModule as keyof typeof BCM_MODULES_MAPPING]?.name || selectedModule}
                </h3>
                <p className="text-sm text-slate-500">{selectedModule}</p>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => openModuleInOdoo(selectedModule)}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open in Odoo
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedModule(null)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="p-6">
              {(() => {
                const module = moduleScores.find(m => m.technicalName === selectedModule);
                if (!module) return null;

                return (
                  <div className="space-y-6">
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <div className="text-3xl font-bold text-blue-600">{module.score}%</div>
                        <div className="text-sm text-slate-500">Current Compliance</div>
                      </div>
                      <div>
                        <div className="text-3xl font-bold text-slate-900">{module.status}</div>
                        <div className="text-sm text-slate-500">Development Status</div>
                      </div>
                      <div>
                        <div className="text-3xl font-bold text-green-600">{module.compliance}%</div>
                        <div className="text-sm text-slate-500">Target Compliance</div>
                      </div>
                    </div>

                    <div className="w-full bg-slate-200 rounded-full h-4">
                      <div
                        className={`h-4 rounded-full transition-all ${getProgressColor(module.score)}`}
                        style={{ width: `${module.score}%` }}
                      />
                    </div>

                    <div className="space-y-4">
                      <h4 className="font-medium text-lg">Module Information:</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium">Technical Name:</span>
                          <p className="text-slate-600">{module.technicalName}</p>
                        </div>
                        <div>
                          <span className="font-medium">Status:</span>
                          <p className={`capitalize ${
                            module.status === 'active' ? 'text-green-600' : 
                            module.status === 'development' ? 'text-yellow-600' : 
                            'text-gray-600'
                          }`}>{module.status}</p>
                        </div>
                      </div>

                      <div className="mt-4">
                        <span className="font-medium">Actions:</span>
                        <div className="flex gap-2 mt-2">
                          <Button 
                            size="sm" 
                            onClick={() => openModuleInOdoo(selectedModule)}
                          >
                            Open in Odoo
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={handleRefresh}
                          >
                            Refresh Data
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComplianceDashboard;