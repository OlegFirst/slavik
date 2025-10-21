import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Settings,
  Shield,
  Globe,
  Bell,
  Save,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Info,
  ExternalLink
} from 'lucide-react';
import { systemConfigService } from '@/services/bcm';

interface ConfigItem {
  id?: number;
  name: string;
  value: string;
  description: string;
  is_active: boolean;
}

const SystemConfigManager: React.FC = () => {
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [editingConfigs, setEditingConfigs] = useState<Record<string, string>>({});

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setLoading(true);
    try {
      console.log('️ Loading system configuration...');
      const configData = await systemConfigService.getSystemConfig();
      setConfig(configData);
      setLastUpdated(configData.lastUpdated);
      console.log(' System config loaded:', configData);
    } catch (error) {
      console.error(' Failed to load config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = (configName: string, value: string) => {
    setEditingConfigs(prev => ({
      ...prev,
      [configName]: value
    }));
  };

  const saveConfig = async (configId: string, configName: string) => {
    setSaving(true);
    try {
      const newValue = editingConfigs[configName];
      if (newValue !== undefined) {
        const success = await systemConfigService.updateConfig(configId, newValue);
        if (success) {
          console.log(` Config ${configName} updated successfully`);
          await loadConfig(); // Reload to get fresh data
          setEditingConfigs(prev => {
            const updated = { ...prev };
            delete updated[configName];
            return updated;
          });
        } else {
          console.error(` Failed to update config ${configName}`);
        }
      }
    } catch (error) {
      console.error('Error saving config:', error);
    } finally {
      setSaving(false);
    }
  };

  const renderConfigSection = (title: string, configs: ConfigItem[], icon: React.ReactNode, color: string) => {
    if (!configs || configs.length === 0) {
      return (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {icon}
              {title}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>No {title.toLowerCase()} settings found in Odoo bcm_config module.</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {icon}
            {title}
          </CardTitle>
          <CardDescription>
            Configuration settings from Odoo bcm_config module (config_type: {title.toLowerCase()})
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {configs.map((configItem, index) => {
            const configKey = `${title.toLowerCase()}_${configItem.name}`;
            const isEditing = editingConfigs[configItem.name] !== undefined;
            const currentValue = isEditing ? editingConfigs[configItem.name] : configItem.value;

            return (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h4 className="font-medium">{configItem.name}</h4>
                    <Badge
                      variant={configItem.is_active ? "default" : "secondary"}
                      className={configItem.is_active ? color : ""}
                    >
                      {configItem.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{configItem.description}</p>

                  <div className="flex items-center gap-2">
                    <Label className="text-xs">Value:</Label>
                    {isEditing ? (
                      <Input
                        value={currentValue}
                        onChange={(e) => handleConfigChange(configItem.name, e.target.value)}
                        className="max-w-xs"
                        size="sm"
                      />
                    ) : (
                      <code className="px-2 py-1 bg-slate-100 rounded text-sm">{currentValue}</code>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {isEditing ? (
                    <>
                      <Button
                        size="sm"
                        onClick={() => saveConfig(configItem.id?.toString() || '', configItem.name)}
                        disabled={saving}
                      >
                        <Save className="h-4 w-4 mr-1" />
                        Save
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setEditingConfigs(prev => {
                            const updated = { ...prev };
                            delete updated[configItem.name];
                            return updated;
                          });
                        }}
                      >
                        Cancel
                      </Button>
                    </>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleConfigChange(configItem.name, configItem.value)}
                    >
                      Edit
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-lg">Loading system configuration...</span>
      </div>
    );
  }

  if (!config) {
    return (
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Configuration Unavailable</AlertTitle>
        <AlertDescription>
          Unable to load system configuration from Odoo bcm_config module.
          Please check the Odoo connection and ensure the bcm_config module is installed.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">BCM System Configuration</h3>
          <p className="text-sm text-muted-foreground">
            Last updated: {new Date(lastUpdated).toLocaleString()}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.open('http://localhost:8069/web#action=bcm_config.action_bcm_config', '_blank')}
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Open in Odoo
          </Button>
          <Button variant="outline" size="sm" onClick={loadConfig}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Configuration Tabs */}
      <Tabs defaultValue="general" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>

        <TabsContent value="general">
          {renderConfigSection(
            'General Settings',
            config.general,
            <Settings className="h-5 w-5" />,
            'bg-blue-100 text-blue-800'
          )}
        </TabsContent>

        <TabsContent value="security">
          {renderConfigSection(
            'Security Settings',
            config.security,
            <Shield className="h-5 w-5" />,
            'bg-red-100 text-red-800'
          )}
        </TabsContent>

        <TabsContent value="integrations">
          {renderConfigSection(
            'Integration Settings',
            config.integrations,
            <Globe className="h-5 w-5" />,
            'bg-green-100 text-green-800'
          )}
        </TabsContent>

        <TabsContent value="notifications">
          {renderConfigSection(
            'Notification Settings',
            config.notifications,
            <Bell className="h-5 w-5" />,
            'bg-orange-100 text-orange-800'
          )}
        </TabsContent>
      </Tabs>

      {/* Connection Status */}
      <Alert>
        <CheckCircle className="h-4 w-4" />
        <AlertTitle>Odoo BCM Integration Status</AlertTitle>
        <AlertDescription>
          Connected to Odoo BCM system on localhost:8069. Configuration data is synchronized with bcm_config module.
          Changes made here will be saved directly to the Odoo database.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default SystemConfigManager;