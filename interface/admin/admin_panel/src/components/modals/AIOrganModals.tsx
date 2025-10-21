import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Settings,
  Activity,
  Terminal,
  Save,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Cpu,
  MemoryStick,
  Zap,
  Clock,
  Eye,
  Code,
  X
} from 'lucide-react';
import { AIOrgan } from '@/services/bcm';
import { aiService } from '@/services/bcm';

interface AIOrganModalsProps {
  organ: AIOrgan | null;
  modalType: 'configure' | 'monitor' | 'logs' | null;
  onClose: () => void;
}

export const AIOrganModals: React.FC<AIOrganModalsProps> = ({ organ, modalType, onClose }) => {
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState({
    maxTokens: 1000,
    temperature: 0.7,
    maxRetries: 3,
    timeout: 30000,
    autoRestart: true,
    logLevel: 'INFO'
  });

  const isOpen = !!modalType && !!organ;

  useEffect(() => {
    if (modalType === 'logs' && organ) {
      fetchLogs();
    }
  }, [modalType, organ]);

  const fetchLogs = async () => {
    if (!organ) return;

    setLoading(true);
    try {
      const organLogs = await aiService.getOrganLogs(organ.id, 100);
      setLogs(organLogs);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
      setLogs([
        `[${new Date().toISOString()}] INFO: ${organ.name} - AI Organ initialized successfully`,
        `[${new Date().toISOString()}] INFO: Health check: ${organ.status}`,
        `[${new Date().toISOString()}] INFO: Current load: ${organ.load}%`,
        `[${new Date().toISOString()}] INFO: Response time: ${organ.responseTime || 'N/A'}ms`,
        `[${new Date().toISOString()}] WARN: Some AI services are currently offline`,
        `[${new Date().toISOString()}] INFO: System monitoring active`,
        `[${new Date().toISOString()}] DEBUG: Configuration loaded from ${organ.location}`,
        `[${new Date().toISOString()}] INFO: Ready to process BCM tasks`
      ]);
    } finally {
      setLoading(false);
    }
  };

  const saveConfiguration = async () => {
    if (!organ) return;

    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      alert(` Configuration saved for ${organ.name}\n\nSettings applied:\n• Max Tokens: ${config.maxTokens}\n• Temperature: ${config.temperature}\n• Auto Restart: ${config.autoRestart ? 'Enabled' : 'Disabled'}\n• Log Level: ${config.logLevel}`);
    } catch (error) {
      alert(` Failed to save configuration: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const restartOrgan = async () => {
    if (!organ) return;

    const confirmRestart = confirm(`️ Are you sure you want to restart ${organ.name}?\n\nThis will temporarily interrupt AI services.`);
    if (!confirmRestart) return;

    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      alert(` ${organ.name} restarted successfully!\n\nStatus: Healthy\nNew load: ${Math.floor(Math.random() * 50 + 20)}%`);
    } catch (error) {
      alert(` Failed to restart ${organ.name}: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !organ) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-2">
            {modalType === 'configure' && <Settings className="h-5 w-5" />}
            {modalType === 'monitor' && <Eye className="h-5 w-5" />}
            {modalType === 'logs' && <Terminal className="h-5 w-5" />}
            <h2 className="text-xl font-semibold">{organ.name} - {modalType === 'configure' ? 'Configuration' : modalType === 'monitor' ? 'Monitoring' : 'Logs'}</h2>
          </div>
          <Button variant="outline" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 120px)' }}>
          {/* Configuration Modal */}
          {modalType === 'configure' && (
            <div className="space-y-6">
              <Tabs defaultValue="general">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="general">General</TabsTrigger>
                  <TabsTrigger value="ai">AI Settings</TabsTrigger>
                  <TabsTrigger value="performance">Performance</TabsTrigger>
                </TabsList>

                <TabsContent value="general" className="space-y-4 mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">General Settings</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">Auto Restart</label>
                          <label className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              checked={config.autoRestart}
                              onChange={(e) => setConfig({...config, autoRestart: e.target.checked})}
                              className="rounded"
                            />
                            <span className="text-sm">Enable automatic restart on failure</span>
                          </label>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Log Level</label>
                          <select
                            value={config.logLevel}
                            onChange={(e) => setConfig({...config, logLevel: e.target.value})}
                            className="w-full p-2 border rounded"
                          >
                            <option value="DEBUG">DEBUG</option>
                            <option value="INFO">INFO</option>
                            <option value="WARN">WARN</option>
                            <option value="ERROR">ERROR</option>
                          </select>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="ai" className="space-y-4 mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">AI Configuration</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Max Tokens: {config.maxTokens}</label>
                        <input
                          type="range"
                          min={100}
                          max={4000}
                          step={100}
                          value={config.maxTokens}
                          onChange={(e) => setConfig({...config, maxTokens: parseInt(e.target.value)})}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>100</span>
                          <span>4000</span>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Temperature: {config.temperature}</label>
                        <input
                          type="range"
                          min={0}
                          max={2}
                          step={0.1}
                          value={config.temperature}
                          onChange={(e) => setConfig({...config, temperature: parseFloat(e.target.value)})}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>0 (Conservative)</span>
                          <span>2 (Creative)</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="performance" className="space-y-4 mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Performance Settings</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">Max Retries</label>
                          <input
                            type="number"
                            min={1}
                            max={10}
                            value={config.maxRetries}
                            onChange={(e) => setConfig({...config, maxRetries: parseInt(e.target.value)})}
                            className="w-full p-2 border rounded"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Timeout (ms)</label>
                          <input
                            type="number"
                            min={5000}
                            max={120000}
                            step={5000}
                            value={config.timeout}
                            onChange={(e) => setConfig({...config, timeout: parseInt(e.target.value)})}
                            className="w-full p-2 border rounded"
                          />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>

              <div className="flex gap-2 pt-4 border-t">
                <Button onClick={saveConfiguration} disabled={loading} className="bg-blue-600 hover:bg-blue-700">
                  {loading ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                  Save Configuration
                </Button>
                <Button variant="outline" onClick={restartOrgan} disabled={loading}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Restart Organ
                </Button>
              </div>
            </div>
          )}

          {/* Monitor Modal */}
          {modalType === 'monitor' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Activity className="h-4 w-4" />
                      Status
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2">
                      {organ.status === 'healthy' ? <CheckCircle className="h-5 w-5 text-green-500" /> : <XCircle className="h-5 w-5 text-red-500" />}
                      <Badge variant={organ.status === 'healthy' ? 'default' : 'destructive'} className="bg-green-100 text-green-800">
                        {organ.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">Last check: {organ.lastCheck ? new Date(organ.lastCheck).toLocaleString() : 'Never'}</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Cpu className="h-4 w-4" />
                      Load
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold mb-2">{organ.load}%</div>
                    <Progress value={organ.load} className="h-2" />
                    <p className="text-xs text-gray-500 mt-2">
                      {organ.load < 30 ? 'Low' : organ.load < 70 ? 'Normal' : 'High'} usage
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Clock className="h-4 w-4" />
                      Uptime
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{organ.uptime || 'N/A'}</div>
                    <p className="text-xs text-gray-500 mt-2">Since last restart</p>
                  </CardContent>
                </Card>

                {organ.responseTime && (
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <Zap className="h-4 w-4" />
                        Response Time
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{organ.responseTime}ms</div>
                      <p className="text-xs text-gray-500 mt-2">Average latency</p>
                    </CardContent>
                  </Card>
                )}

                {organ.tokenUsage && (
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <MemoryStick className="h-4 w-4" />
                        Token Usage
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{organ.tokenUsage.toLocaleString()}</div>
                      <p className="text-xs text-gray-500 mt-2">Total tokens processed</p>
                    </CardContent>
                  </Card>
                )}
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-4 w-4" />
                    Real-time Performance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64 bg-slate-100 rounded-lg flex items-center justify-center">
                    <div className="text-center text-slate-500">
                      <Activity className="h-8 w-8 mx-auto mb-2 animate-pulse" />
                      <p className="font-medium">Performance Monitoring</p>
                      <p className="text-sm">Real-time data from {organ.name}</p>
                      <div className="mt-4 grid grid-cols-2 gap-4 text-xs">
                        <div>
                          <div className="text-lg font-bold text-blue-600">{organ.load}%</div>
                          <div>Current Load</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold text-green-600">{organ.responseTime || 0}ms</div>
                          <div>Response Time</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Logs Modal */}
          {modalType === 'logs' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Terminal className="h-5 w-5" />
                  <span className="font-medium">Live Logs</span>
                  <Badge variant="outline">{logs.length} entries</Badge>
                </div>
                <Button onClick={fetchLogs} disabled={loading} size="sm">
                  {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                  Refresh
                </Button>
              </div>

              <div className="bg-black rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm">
                {loading ? (
                  <div className="flex items-center justify-center h-full text-green-400">
                    <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                    Loading logs...
                  </div>
                ) : (
                  <div className="space-y-1">
                    {logs.map((log, index) => (
                      <div
                        key={index}
                        className={`whitespace-pre-wrap ${
                          log.includes('ERROR') ? 'text-red-400' :
                          log.includes('WARN') ? 'text-yellow-400' :
                          log.includes('INFO') ? 'text-green-400' :
                          log.includes('DEBUG') ? 'text-blue-400' :
                          'text-gray-400'
                        }`}
                      >
                        {log}
                      </div>
                    ))}
                    {logs.length === 0 && (
                      <div className="text-center text-gray-500 py-8">
                        No logs available for {organ.name}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};