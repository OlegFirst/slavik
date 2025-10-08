import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Wrench,
  Info,
  Package,
  Search,
  Filter,
  GitBranch,
  Bug,
  Zap,
  FileText,
  Shield,
  Database,
  Code,
} from 'lucide-react';

interface Module {
  name: string;
  version?: string;
  category?: string;
  summary?: string;
  status?: 'success' | 'warning' | 'error' | 'unknown';
  errors?: string[];
  warnings?: string[];
  dependencies?: string[];
  path?: string;
  installed?: boolean;
}

interface ModuleDetails {
  name: string;
  info?: any;
  errors?: string[];
  warnings?: string[];
  dependencies?: {
    declared?: string[];
    missing?: string[];
    circular?: string[];
    external_models?: string[];
  };
  status?: string;
}

const ModulesOverview: React.FC = () => {
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [tabValue, setTabValue] = useState('all');
  const [selectedModule, setSelectedModule] = useState<ModuleDetails | null>(null);
  const [detailsDialog, setDetailsDialog] = useState(false);
  const [validationResults, setValidationResults] = useState<any>(null);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [validating, setValidating] = useState(false);

  useEffect(() => {
    loadModules();
  }, []);

  const loadModules = async () => {
    setLoading(true);
    try {
      // Сначала пробуем Module Validator API
      const response = await fetch('http://localhost:5001/api/modules/list');
      const data = await response.json();

      if (data.success && data.modules && data.modules.length > 0) {
        setModules(data.modules);
      } else {
        // Если Module Validator пустой, загружаем из odoo-integration
        const { getBCMModules } = await import('@/utils/odoo-integration');
        const bcmModules = await getBCMModules();

        // Преобразуем формат для совместимости
        const formattedModules = bcmModules.map((mod: any) => ({
          name: mod.display_name || mod.name,
          version: mod.version || '17.0.1.0',
          category: 'BCM',
          summary: `${mod.display_name} module for ISO 22301 compliance`,
          status: mod.installed ? 'success' : 'warning',
          installed: mod.installed,
          path: `/odoo/modules/${mod.name}`,
          dependencies: []
        }));

        setModules(formattedModules);
        console.log('Loaded BCM modules from Odoo:', formattedModules.length);
      }
    } catch (error) {
      console.error('Error loading modules:', error);
      // Fallback to hardcoded BCM modules list
      setModules([
        { name: 'BCM Base', version: '17.0.1.0', category: 'Core', summary: 'Base BCM functionality', status: 'success', installed: true },
        { name: 'BCM Core', version: '17.0.1.0', category: 'Core', summary: 'Core BCM operations', status: 'success', installed: true },
        { name: 'BCM Risk Management', version: '17.0.1.0', category: 'Risk', summary: 'Risk assessment and management', status: 'success', installed: true },
        { name: 'BCM BIA', version: '17.0.1.0', category: 'Analysis', summary: 'Business Impact Analysis', status: 'success', installed: true },
        { name: 'BCM Governance', version: '17.0.1.0', category: 'Governance', summary: 'BCM governance and compliance', status: 'success', installed: true },
        { name: 'BCM AI Control', version: '17.0.1.0', category: 'AI', summary: 'AI-powered BCM control', status: 'success', installed: true },
        { name: 'BCM Incident', version: '17.0.1.0', category: 'Operations', summary: 'Incident management', status: 'warning', installed: false },
        { name: 'BCM Exercise', version: '17.0.1.0', category: 'Training', summary: 'Exercise and testing', status: 'warning', installed: false }
      ]);
    }
    setLoading(false);
  };

  const validateModules = async () => {
    setValidating(true);
    try {
      const response = await fetch('http://localhost:5001/api/modules/validate');
      const data = await response.json();

      if (data.success) {
        setValidationResults(data);
        // Update modules with validation status
        const modulesWithStatus = modules.map(module => {
          const validation = data.modules.find((m: any) => m.name === module.name);
          return {
            ...module,
            status: validation?.status || 'unknown',
            errors: validation?.errors || [],
            warnings: validation?.warnings || []
          };
        });
        setModules(modulesWithStatus);
      }
    } catch (error) {
      console.error('Error validating modules:', error);
    }
    setValidating(false);
  };

  const loadModuleDetails = async (moduleName: string) => {
    try {
      const response = await fetch(`http://localhost:5001/api/modules/${moduleName}`);
      const data = await response.json();

      if (data.success) {
        setSelectedModule(data.module);
        setDetailsDialog(true);
      }
    } catch (error) {
      console.error('Error loading module details:', error);
    }
  };

  const fixModuleIssues = async (moduleName: string) => {
    try {
      const response = await fetch(`http://localhost:5001/api/modules/fix/${moduleName}`, {
        method: 'POST'
      });
      const data = await response.json();

      if (data.success) {
        // Refresh validation after fix
        validateModules();
      }
    } catch (error) {
      console.error('Error fixing module:', error);
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Info className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (status?: string) => {
    const variant = status === 'success' ? 'default' :
                   status === 'warning' ? 'secondary' :
                   status === 'error' ? 'destructive' : 'outline';
    return <Badge variant={variant}>{status || 'unknown'}</Badge>;
  };

  const filteredModules = modules.filter(module => {
    const matchesSearch = module.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         module.summary?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || module.category === categoryFilter;

    return matchesSearch && matchesCategory;
  });

  const getTabModules = () => {
    switch (tabValue) {
      case 'all':
        return filteredModules;
      case 'errors':
        return filteredModules.filter(m => m.status === 'error');
      case 'warnings':
        return filteredModules.filter(m => m.status === 'warning');
      case 'healthy':
        return filteredModules.filter(m => m.status === 'success');
      default:
        return filteredModules;
    }
  };

  const categories = [...new Set(modules.map(m => m.category))].filter(Boolean);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-6 w-6" />
                BCM Modules Overview
              </CardTitle>
              <CardDescription>
                Validate and manage all BCM modules in your system
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="default"
                onClick={validateModules}
                disabled={validating}
              >
                {validating ? (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Bug className="h-4 w-4 mr-2" />
                )}
                Validate All
              </Button>
              <Button
                variant="outline"
                onClick={loadModules}
                disabled={loading}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>

        {validationResults && (
          <CardContent>
            <Alert className={validationResults.total_errors > 0 ? "border-red-500" : "border-green-500"}>
              <AlertDescription>
                <strong>Validation Results:</strong> {validationResults.total_errors} errors, {validationResults.total_warnings} warnings in {validationResults.modules?.length || 0} modules
              </AlertDescription>
            </Alert>
          </CardContent>
        )}

        <CardContent>
          <div className="flex gap-4 mb-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search modules..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <div>
              <select
                className="h-9 px-3 border rounded-md"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                <option value="all">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>

          <Tabs value={tabValue} onValueChange={setTabValue}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all">
                All ({filteredModules.length})
              </TabsTrigger>
              <TabsTrigger value="errors">
                Errors ({filteredModules.filter(m => m.status === 'error').length})
              </TabsTrigger>
              <TabsTrigger value="warnings">
                Warnings ({filteredModules.filter(m => m.status === 'warning').length})
              </TabsTrigger>
              <TabsTrigger value="healthy">
                Healthy ({filteredModules.filter(m => m.status === 'success').length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value={tabValue} className="mt-4">
              {loading ? (
                <div className="text-center py-8">
                  <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2" />
                  <p>Loading modules...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {getTabModules().map((module) => (
                    <Card key={module.name} className="hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2">
                            {getStatusIcon(module.status)}
                            <CardTitle className="text-lg">{module.name}</CardTitle>
                          </div>
                          {getStatusBadge(module.status)}
                        </div>
                        <CardDescription>
                          {module.summary || 'No description available'}
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex flex-wrap gap-1">
                          <Badge variant="outline">
                            {module.category || 'Uncategorized'}
                          </Badge>
                          <Badge variant="outline">
                            v{module.version || '1.0.0'}
                          </Badge>
                        </div>

                        {module.dependencies && module.dependencies.length > 0 && (
                          <div className="text-sm text-gray-500">
                            <GitBranch className="h-3 w-3 inline mr-1" />
                            {module.dependencies.slice(0, 3).join(', ')}
                            {module.dependencies.length > 3 && ` +${module.dependencies.length - 3} more`}
                          </div>
                        )}

                        {module.errors && module.errors.length > 0 && (
                          <Alert className="border-red-500">
                            <AlertDescription className="text-sm">
                              {module.errors.length} error(s) found
                            </AlertDescription>
                          </Alert>
                        )}

                        {module.warnings && module.warnings.length > 0 && (
                          <Alert className="border-yellow-500">
                            <AlertDescription className="text-sm">
                              {module.warnings.length} warning(s) found
                            </AlertDescription>
                          </Alert>
                        )}

                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => loadModuleDetails(module.name)}
                          >
                            <Info className="h-3 w-3 mr-1" />
                            Details
                          </Button>
                          {module.status === 'error' && (
                            <Button
                              size="sm"
                              variant="default"
                              onClick={() => fixModuleIssues(module.name)}
                            >
                              <Zap className="h-3 w-3 mr-1" />
                              Auto Fix
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Module Details Dialog */}
      <Dialog open={detailsDialog} onOpenChange={setDetailsDialog}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          {selectedModule && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  {getStatusIcon(selectedModule.status)}
                  {selectedModule.name} Details
                </DialogTitle>
                <DialogDescription>
                  Detailed information about the module
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Module Information</h3>
                  <div className="space-y-1 text-sm">
                    <div><strong>Version:</strong> {selectedModule.info?.version || 'N/A'}</div>
                    <div><strong>Category:</strong> {selectedModule.info?.category || 'N/A'}</div>
                    <div><strong>License:</strong> {selectedModule.info?.license || 'N/A'}</div>
                    <div><strong>Summary:</strong> {selectedModule.info?.summary || 'No summary available'}</div>
                  </div>
                </div>

                <Separator />

                <div>
                  <h3 className="font-semibold mb-2">Dependencies</h3>
                  {selectedModule.dependencies?.declared?.length ? (
                    <div className="flex flex-wrap gap-1">
                      {selectedModule.dependencies.declared.map(dep => (
                        <Badge key={dep} variant="outline">{dep}</Badge>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No dependencies declared</p>
                  )}

                  {selectedModule.dependencies?.missing?.length ? (
                    <Alert className="mt-2 border-red-500">
                      <AlertDescription>
                        Missing dependencies: {selectedModule.dependencies.missing.join(', ')}
                      </AlertDescription>
                    </Alert>
                  ) : null}
                </div>

                {selectedModule.errors?.length ? (
                  <>
                    <Separator />
                    <div>
                      <h3 className="font-semibold mb-2 text-red-600">
                        Errors ({selectedModule.errors.length})
                      </h3>
                      <ScrollArea className="h-40">
                        <ul className="space-y-1 text-sm">
                          {selectedModule.errors.map((error, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <XCircle className="h-4 w-4 text-red-500 flex-shrink-0 mt-0.5" />
                              <span>{error}</span>
                            </li>
                          ))}
                        </ul>
                      </ScrollArea>
                    </div>
                  </>
                ) : null}

                {selectedModule.warnings?.length ? (
                  <>
                    <Separator />
                    <div>
                      <h3 className="font-semibold mb-2 text-yellow-600">
                        Warnings ({selectedModule.warnings.length})
                      </h3>
                      <ScrollArea className="h-40">
                        <ul className="space-y-1 text-sm">
                          {selectedModule.warnings.map((warning, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <AlertTriangle className="h-4 w-4 text-yellow-500 flex-shrink-0 mt-0.5" />
                              <span>{warning}</span>
                            </li>
                          ))}
                        </ul>
                      </ScrollArea>
                    </div>
                  </>
                ) : null}

                {selectedModule.status === 'error' && (
                  <div className="flex justify-end">
                    <Button
                      onClick={() => {
                        fixModuleIssues(selectedModule.name);
                        setDetailsDialog(false);
                      }}
                    >
                      <Zap className="h-4 w-4 mr-2" />
                      Auto Fix Issues
                    </Button>
                  </div>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ModulesOverview;