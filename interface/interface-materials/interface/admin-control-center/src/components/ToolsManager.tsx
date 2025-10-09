/**
 * Tools Manager Component
 * =======================
 *
 * Manage and execute platform tools through the UI
 * NO MOCK DATA - Real integration with Analytics Specialist
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toolsService, type Tool } from '@/services/realtime';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Play,
  Square,
  History,
  FileText,
  AlertCircle,
  CheckCircle2,
  Loader2,
} from 'lucide-react';

export const ToolsManager: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [executionResult, setExecutionResult] = useState<any>(null);

  // Fetch available tools
  const { data: tools = [], isLoading } = useQuery({
    queryKey: ['tools'],
    queryFn: () => toolsService.listTools(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Run tool mutation
  const runToolMutation = useMutation({
    mutationFn: ({ toolName, params }: { toolName: string; params?: any }) =>
      toolsService.runTool(toolName, params),
    onSuccess: (data, variables) => {
      setExecutionResult(data);
      queryClient.invalidateQueries({ queryKey: ['tools'] });
      queryClient.invalidateQueries({ queryKey: ['tool-history', variables.toolName] });
    },
  });

  // Fetch tool history when selected
  const { data: toolHistory = [] } = useQuery({
    queryKey: ['tool-history', selectedTool],
    queryFn: () => toolsService.getToolHistory(selectedTool!),
    enabled: !!selectedTool,
  });

  // Fetch tool results when selected
  const { data: toolResults } = useQuery({
    queryKey: ['tool-results', selectedTool],
    queryFn: () => toolsService.getToolResults(selectedTool!),
    enabled: !!selectedTool,
  });

  const handleRunTool = (toolName: string) => {
    runToolMutation.mutate({ toolName });
  };

  // Group tools by category
  const toolsByCategory = tools.reduce((acc, tool) => {
    if (!acc[tool.category]) {
      acc[tool.category] = [];
    }
    acc[tool.category].push(tool);
    return acc;
  }, {} as Record<string, Tool[]>);

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'running':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Square className="w-4 h-4 text-gray-400" />;
    }
  };

  const getCompetencyBadge = (competency: string) => {
    const colors = {
      junior: 'bg-green-100 text-green-800',
      middle: 'bg-blue-100 text-blue-800',
      senior: 'bg-purple-100 text-purple-800',
      expert: 'bg-red-100 text-red-800',
    };
    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium ${
          colors[competency as keyof typeof colors] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {competency}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tools Management</h1>
          <p className="text-gray-600">Execute and manage platform analysis tools</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">{tools.length} tools available</span>
        </div>
      </div>

      <Tabs defaultValue="all" className="w-full">
        <TabsList>
          <TabsTrigger value="all">All Tools</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="quality">Quality</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
        </TabsList>

        {/* All Tools */}
        <TabsContent value="all" className="space-y-4">
          {Object.entries(toolsByCategory).map(([category, categoryTools]) => (
            <Card key={category}>
              <CardHeader>
                <CardTitle className="text-lg capitalize">{category} Tools</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {categoryTools.map((tool) => (
                    <div
                      key={tool.name}
                      className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => setSelectedTool(tool.name)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(tool.status)}
                          <h3 className="font-semibold text-gray-900">{tool.name}</h3>
                        </div>
                        {getCompetencyBadge(tool.competency_required)}
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{tool.description}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">
                          {tool.last_run
                            ? `Last run: ${new Date(tool.last_run).toLocaleString()}`
                            : 'Never run'}
                        </span>
                        <Button
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRunTool(tool.name);
                          }}
                          disabled={runToolMutation.isPending}
                        >
                          <Play className="w-3 h-3 mr-1" />
                          Run
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Category-specific tabs */}
        {(['analysis', 'security', 'quality', 'monitoring'] as const).map((category) => (
          <TabsContent key={category} value={category} className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="capitalize">{category} Tools</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {toolsByCategory[category]?.map((tool) => (
                    <div
                      key={tool.name}
                      className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => setSelectedTool(tool.name)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(tool.status)}
                          <h3 className="font-semibold text-gray-900">{tool.name}</h3>
                        </div>
                        {getCompetencyBadge(tool.competency_required)}
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{tool.description}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">
                          {tool.last_run
                            ? `Last run: ${new Date(tool.last_run).toLocaleString()}`
                            : 'Never run'}
                        </span>
                        <Button
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRunTool(tool.name);
                          }}
                          disabled={runToolMutation.isPending}
                        >
                          <Play className="w-3 h-3 mr-1" />
                          Run
                        </Button>
                      </div>
                    </div>
                  )) || <p className="text-gray-500">No {category} tools available</p>}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* Tool Details Modal */}
      {selectedTool && (
        <Card className="mt-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{selectedTool} Details</CardTitle>
              <Button variant="outline" size="sm" onClick={() => setSelectedTool(null)}>
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="results" className="w-full">
              <TabsList>
                <TabsTrigger value="results">
                  <FileText className="w-4 h-4 mr-2" />
                  Results
                </TabsTrigger>
                <TabsTrigger value="history">
                  <History className="w-4 h-4 mr-2" />
                  History
                </TabsTrigger>
              </TabsList>

              <TabsContent value="results" className="mt-4">
                {toolResults ? (
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-96 text-sm">
                    {JSON.stringify(toolResults, null, 2)}
                  </pre>
                ) : (
                  <p className="text-gray-500">No results available. Run the tool to see results.</p>
                )}
              </TabsContent>

              <TabsContent value="history" className="mt-4">
                {toolHistory.length > 0 ? (
                  <div className="space-y-2">
                    {toolHistory.map((entry, index) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">
                            {new Date(entry.timestamp).toLocaleString()}
                          </span>
                          <span
                            className={`px-2 py-1 rounded text-xs ${
                              entry.status === 'success'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {entry.status}
                          </span>
                        </div>
                        {entry.output && (
                          <p className="text-sm text-gray-600 mt-1">{entry.output}</p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No execution history available</p>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* Execution Result Toast */}
      {executionResult && (
        <div className="fixed bottom-4 right-4 bg-white shadow-lg rounded-lg p-4 max-w-md border border-green-200">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-gray-900">Tool Executed Successfully</h4>
              <p className="text-sm text-gray-600 mt-1">
                {executionResult.message || 'Tool completed execution'}
              </p>
              <Button
                variant="outline"
                size="sm"
                className="mt-2"
                onClick={() => setExecutionResult(null)}
              >
                Dismiss
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolsManager;
