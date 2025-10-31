'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import {
  Settings,
  Users,
  Database,
  Mail,
  Bell,
  Shield,
  Key,
  Globe,
  Server,
  Activity,
  Clock,
  Zap,
  FileText,
  Download,
  Upload,
  RefreshCw,
  Save,
  RotateCcw,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Archive,
  Play,
  Eye,
  EyeOff,
  Copy,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  Info,
  HardDrive,
  Wifi,
  Calendar,
  Target,
  Building,
  Phone,
  MapPin
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useBCMStore } from '@/lib/bcm-store'

// Types
interface SystemConfig {
  id: string
  category: 'general' | 'security' | 'notification' | 'integration' | 'backup' | 'performance'
  key: string
  name: string
  description: string
  value: any
  defaultValue: any
  type: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'password' | 'email' | 'url'
  validation?: ConfigValidation
  isRequired: boolean
  isReadOnly: boolean
  lastModified: string
  modifiedBy: string
  environment: 'development' | 'staging' | 'production' | 'all'
  tags: string[]
}

interface ConfigValidation {
  min?: number
  max?: number
  pattern?: string
  options?: string[]
  message?: string
}

interface UserProfile {
  id: string
  username: string
  email: string
  firstName: string
  lastName: string
  role: string
  department: string
  permissions: string[]
  preferences: UserPreferences
  lastLogin?: string
  isActive: boolean
  twoFactorEnabled: boolean
  avatar?: string
}

interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: string
  timezone: string
  dateFormat: string
  notifications: NotificationSettings
  dashboard: DashboardSettings
}

interface NotificationSettings {
  email: boolean
  browser: boolean
  mobile: boolean
  frequency: 'immediate' | 'hourly' | 'daily' | 'weekly'
  types: string[]
}

interface DashboardSettings {
  defaultView: string
  refreshInterval: number
  widgets: string[]
  layout: string
}

interface SystemIntegration {
  id: string
  name: string
  type: 'api' | 'webhook' | 'email' | 'sms' | 'database' | 'file_system'
  status: 'active' | 'inactive' | 'error' | 'testing'
  endpoint?: string
  authentication: IntegrationAuth
  configuration: any
  lastSync?: string
  errorCount: number
  isEnabled: boolean
  description: string
}

interface IntegrationAuth {
  type: 'api_key' | 'oauth' | 'basic' | 'token'
  credentials: any
  expiresAt?: string
}

interface BackupConfig {
  id: string
  name: string
  type: 'full' | 'incremental' | 'differential'
  schedule: string
  retention: number
  destination: string
  encryption: boolean
  compression: boolean
  isEnabled: boolean
  lastBackup?: string
  nextBackup?: string
  size?: number
  status: 'success' | 'running' | 'failed' | 'pending'
}

interface AuditLog {
  id: string
  timestamp: string
  user: string
  action: string
  resource: string
  details: any
  ipAddress: string
  userAgent: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  category: 'authentication' | 'configuration' | 'data' | 'system'
}

// Mock data
const generateMockConfigs = (): SystemConfig[] => {
  return [
    {
      id: 'CFG-001',
      category: 'general',
      key: 'system.name',
      name: 'System Name',
      description: 'Display name for the BCM platform',
      value: 'BCM Enterprise Platform',
      defaultValue: 'BCM Platform',
      type: 'string',
      isRequired: true,
      isReadOnly: false,
      lastModified: '2024-01-15T10:30:00Z',
      modifiedBy: 'System Admin',
      environment: 'all',
      tags: ['branding', 'display']
    },
    {
      id: 'CFG-002',
      category: 'security',
      key: 'auth.session_timeout',
      name: 'Session Timeout',
      description: 'User session timeout in minutes',
      value: 60,
      defaultValue: 30,
      type: 'number',
      validation: { min: 5, max: 480 },
      isRequired: true,
      isReadOnly: false,
      lastModified: '2024-01-10T14:20:00Z',
      modifiedBy: 'Security Admin',
      environment: 'all',
      tags: ['security', 'authentication']
    },
    {
      id: 'CFG-003',
      category: 'notification',
      key: 'email.smtp_server',
      name: 'SMTP Server',
      description: 'Email server configuration for notifications',
      value: 'smtp.company.com',
      defaultValue: 'localhost',
      type: 'string',
      isRequired: true,
      isReadOnly: false,
      lastModified: '2024-01-05T09:15:00Z',
      modifiedBy: 'IT Admin',
      environment: 'production',
      tags: ['email', 'notification']
    },
    {
      id: 'CFG-004',
      category: 'integration',
      key: 'api.rate_limit',
      name: 'API Rate Limit',
      description: 'Maximum API requests per hour per user',
      value: 1000,
      defaultValue: 500,
      type: 'number',
      validation: { min: 100, max: 10000 },
      isRequired: true,
      isReadOnly: false,
      lastModified: '2024-01-12T16:45:00Z',
      modifiedBy: 'API Admin',
      environment: 'all',
      tags: ['api', 'performance']
    }
  ]
}

const generateMockUsers = (): UserProfile[] => {
  return [
    {
      id: 'USR-001',
      username: 'admin',
      email: 'admin@company.com',
      firstName: 'System',
      lastName: 'Administrator',
      role: 'System Admin',
      department: 'IT',
      permissions: ['*'],
      preferences: {
        theme: 'light',
        language: 'en',
        timezone: 'UTC',
        dateFormat: 'DD/MM/YYYY',
        notifications: {
          email: true,
          browser: true,
          mobile: false,
          frequency: 'immediate',
          types: ['security', 'system', 'backup']
        },
        dashboard: {
          defaultView: 'executive',
          refreshInterval: 300,
          widgets: ['incidents', 'metrics', 'alerts'],
          layout: 'grid'
        }
      },
      lastLogin: '2024-01-15T08:30:00Z',
      isActive: true,
      twoFactorEnabled: true
    },
    {
      id: 'USR-002',
      username: 'bcm.manager',
      email: 'bcm@company.com',
      firstName: 'Jane',
      lastName: 'Smith',
      role: 'BCM Manager',
      department: 'Business Continuity',
      permissions: ['bcm.*', 'reports.read', 'incidents.*'],
      preferences: {
        theme: 'auto',
        language: 'en',
        timezone: 'America/New_York',
        dateFormat: 'MM/DD/YYYY',
        notifications: {
          email: true,
          browser: true,
          mobile: true,
          frequency: 'immediate',
          types: ['incidents', 'plans', 'compliance']
        },
        dashboard: {
          defaultView: 'operational',
          refreshInterval: 60,
          widgets: ['plans', 'incidents', 'compliance'],
          layout: 'list'
        }
      },
      lastLogin: '2024-01-15T07:45:00Z',
      isActive: true,
      twoFactorEnabled: false
    }
  ]
}

const generateMockIntegrations = (): SystemIntegration[] => {
  return [
    {
      id: 'INT-001',
      name: 'Slack Notifications',
      type: 'webhook',
      status: 'active',
      endpoint: 'https://hooks.slack.com/services/...',
      authentication: {
        type: 'token',
        credentials: { token: 'xoxb-...' }
      },
      configuration: {
        channels: ['#bcm-alerts', '#incidents'],
        events: ['incident.created', 'plan.tested']
      },
      lastSync: '2024-01-15T10:30:00Z',
      errorCount: 0,
      isEnabled: true,
      description: 'Send BCM alerts to Slack channels'
    },
    {
      id: 'INT-002',
      name: 'External SIEM',
      type: 'api',
      status: 'inactive',
      endpoint: 'https://siem.company.com/api/v1',
      authentication: {
        type: 'api_key',
        credentials: { apiKey: 'sk_...' }
      },
      configuration: {
        logTypes: ['security', 'audit'],
        batchSize: 100
      },
      errorCount: 3,
      isEnabled: false,
      description: 'Forward security logs to external SIEM'
    }
  ]
}

const generateMockBackups = (): BackupConfig[] => {
  return [
    {
      id: 'BCK-001',
      name: 'Daily Full Backup',
      type: 'full',
      schedule: '0 2 * * *',
      retention: 30,
      destination: 's3://backup-bucket/bcm',
      encryption: true,
      compression: true,
      isEnabled: true,
      lastBackup: '2024-01-15T02:00:00Z',
      nextBackup: '2024-01-16T02:00:00Z',
      size: 2048000000,
      status: 'success'
    },
    {
      id: 'BCK-002',
      name: 'Hourly Incremental',
      type: 'incremental',
      schedule: '0 * * * *',
      retention: 7,
      destination: 's3://backup-bucket/bcm/incremental',
      encryption: true,
      compression: true,
      isEnabled: true,
      lastBackup: '2024-01-15T10:00:00Z',
      nextBackup: '2024-01-15T11:00:00Z',
      size: 52428800,
      status: 'success'
    }
  ]
}

export function ConfigurationModule() {
  const queryClient = useQueryClient()
  const { publishEvent } = useBCMStore()

  const [activeTab, setActiveTab] = useState<'system' | 'users' | 'integrations' | 'backup' | 'audit'>('system')
  const [selectedConfig, setSelectedConfig] = useState<SystemConfig | null>(null)
  const [selectedUser, setSelectedUser] = useState<UserProfile | null>(null)
  const [showNewUserDialog, setShowNewUserDialog] = useState(false)
  const [showPasswordDialog, setShowPasswordDialog] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [unsavedChanges, setUnsavedChanges] = useState<Record<string, any>>({})

  // Fetch system configurations
  const { data: configs = [], isLoading: configsLoading } = useQuery({
    queryKey: ['system-configs'],
    queryFn: async () => {
      // API client doesn't have get method, using mock data
      return generateMockConfigs()
    }
  })

  // Fetch users
  const { data: users = [] } = useQuery({
    queryKey: ['system-users'],
    queryFn: async () => {
      // API client doesn't have get method, using mock data
      return generateMockUsers()
    }
  })

  // Fetch integrations
  const { data: integrations = [] } = useQuery({
    queryKey: ['system-integrations'],
    queryFn: async () => {
      // API client doesn't have get method, using mock data
      return generateMockIntegrations()
    }
  })

  // Fetch backups
  const { data: backups = [] } = useQuery({
    queryKey: ['system-backups'],
    queryFn: async () => {
      // API client doesn't have get method, using mock data
      return generateMockBackups()
    }
  })

  // Calculate system metrics
  const systemMetrics = {
    totalConfigs: configs.length,
    modifiedToday: configs.filter((c: SystemConfig) =>
      new Date(c.lastModified).toDateString() === new Date().toDateString()
    ).length,
    activeUsers: users.filter((u: UserProfile) => u.isActive).length,
    totalUsers: users.length,
    activeIntegrations: integrations.filter((i: SystemIntegration) => i.status === 'active').length,
    totalIntegrations: integrations.length,
    backupStatus: backups.filter((b: BackupConfig) => b.status === 'success').length / (backups.length || 1) * 100,
    lastBackup: backups.length > 0 ? Math.max(...backups.map(b => new Date(b.lastBackup || 0).getTime())) : 0
  }

  // Filter configurations
  const filteredConfigs = configs.filter((config: SystemConfig) => {
    const matchesSearch = config.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         config.key.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         config.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = filterCategory === 'all' || config.category === filterCategory
    return matchesSearch && matchesCategory
  })

  // Update configuration value
  const updateConfig = (configId: string, newValue: any) => {
    setUnsavedChanges({
      ...unsavedChanges,
      [configId]: newValue
    })
  }

  // Save configuration changes
  const saveConfigMutation = useMutation({
    mutationFn: async (changes: Record<string, any>) => {
      // API client doesn't have post method, simulating success
      return { success: true, data: changes }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system-configs'] })
      setUnsavedChanges({})
      publishEvent({
        type: 'system_alert',
        source: 'configuration',
        data: { message: 'Configuration updated successfully' }
      })
    }
  })

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'success': return 'bg-green-500'
      case 'inactive':
      case 'pending': return 'bg-yellow-500'
      case 'error':
      case 'failed': return 'bg-red-500'
      case 'running':
      case 'testing': return 'bg-blue-500'
      default: return 'bg-gray-500'
    }
  }

  // Format file size
  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    if (bytes === 0) return '0 Bytes'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">System Configuration</h1>
          <p className="text-muted-foreground mt-1">
            Manage system settings, users, and integrations
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => queryClient.invalidateQueries()}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          {Object.keys(unsavedChanges).length > 0 && (
            <Button
              onClick={() => saveConfigMutation.mutate(unsavedChanges)}
              disabled={saveConfigMutation.isPending}
            >
              <Save className="w-4 h-4 mr-2" />
              Save Changes ({Object.keys(unsavedChanges).length})
            </Button>
          )}
        </div>
      </div>

      {/* Unsaved Changes Alert */}
      {Object.keys(unsavedChanges).length > 0 && (
        <Alert className="border-yellow-500 bg-yellow-50">
          <AlertTriangle className="h-4 w-4 text-yellow-600" />
          <AlertDescription className="text-yellow-800">
            You have {Object.keys(unsavedChanges).length} unsaved configuration change{Object.keys(unsavedChanges).length > 1 ? 's' : ''}.
            Don't forget to save your changes.
          </AlertDescription>
        </Alert>
      )}

      {/* System Metrics Overview */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Users
              </CardTitle>
              <Users className="w-4 h-4 text-blue-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{systemMetrics.activeUsers}</div>
            <div className="text-xs text-muted-foreground mt-1">
              of {systemMetrics.totalUsers} total users
            </div>
            <Progress value={systemMetrics.activeUsers / systemMetrics.totalUsers * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Integrations
              </CardTitle>
              <Globe className="w-4 h-4 text-green-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{systemMetrics.activeIntegrations}</div>
            <div className="text-xs text-muted-foreground mt-1">
              of {systemMetrics.totalIntegrations} configured
            </div>
            <Progress value={systemMetrics.activeIntegrations / systemMetrics.totalIntegrations * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Backup Status
              </CardTitle>
              <HardDrive className="w-4 h-4 text-purple-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{Math.round(systemMetrics.backupStatus)}%</div>
            <div className="text-xs text-muted-foreground mt-1">
              Success rate
            </div>
            <Progress value={systemMetrics.backupStatus} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Configurations
              </CardTitle>
              <Settings className="w-4 h-4 text-orange-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{systemMetrics.totalConfigs}</div>
            <div className="text-xs text-muted-foreground mt-1">
              {systemMetrics.modifiedToday} modified today
            </div>
            <Progress value={systemMetrics.modifiedToday / systemMetrics.totalConfigs * 100} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)}>
        <TabsList className="grid grid-cols-5 w-full">
          <TabsTrigger value="system">System Settings</TabsTrigger>
          <TabsTrigger value="users">User Management</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="backup">Backup & Recovery</TabsTrigger>
          <TabsTrigger value="audit">Audit Logs</TabsTrigger>
        </TabsList>

        <TabsContent value="system" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>System Configuration</CardTitle>
                  <CardDescription>Manage core system settings and parameters</CardDescription>
                </div>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search settings..."
                      className="pl-8 w-64"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                  <Select value={filterCategory} onValueChange={setFilterCategory}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      <SelectItem value="general">General</SelectItem>
                      <SelectItem value="security">Security</SelectItem>
                      <SelectItem value="notification">Notification</SelectItem>
                      <SelectItem value="integration">Integration</SelectItem>
                      <SelectItem value="backup">Backup</SelectItem>
                      <SelectItem value="performance">Performance</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {['general', 'security', 'notification', 'integration', 'backup', 'performance'].map((category) => {
                  const categoryConfigs = filteredConfigs.filter((c: SystemConfig) => c.category === category)
                  if (categoryConfigs.length === 0) return null

                  return (
                    <div key={category} className="border rounded-lg p-4">
                      <h3 className="text-lg font-medium mb-3 capitalize flex items-center gap-2">
                        {category === 'general' && <Settings className="w-5 h-5" />}
                        {category === 'security' && <Shield className="w-5 h-5" />}
                        {category === 'notification' && <Bell className="w-5 h-5" />}
                        {category === 'integration' && <Globe className="w-5 h-5" />}
                        {category === 'backup' && <HardDrive className="w-5 h-5" />}
                        {category === 'performance' && <Activity className="w-5 h-5" />}
                        {category.replace('_', ' ')} Settings
                      </h3>
                      <div className="space-y-3">
                        {categoryConfigs.map((config: SystemConfig) => {
                          const currentValue = unsavedChanges[config.id] ?? config.value
                          const hasChanges = unsavedChanges[config.id] !== undefined

                          return (
                            <div key={config.id} className={`p-3 border rounded ${hasChanges ? 'border-yellow-500 bg-yellow-50' : ''}`}>
                              <div className="flex justify-between items-start mb-2">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2">
                                    <Label className="font-medium">{config.name}</Label>
                                    {config.isRequired && <Badge variant="outline" className="text-xs">Required</Badge>}
                                    {config.isReadOnly && <Badge variant="outline" className="text-xs">Read Only</Badge>}
                                    {hasChanges && <Badge className="bg-yellow-500 text-xs">Modified</Badge>}
                                  </div>
                                  <div className="text-sm text-muted-foreground mt-1">
                                    {config.description}
                                  </div>
                                  <div className="text-xs text-muted-foreground">
                                    Key: {config.key} • Modified by {config.modifiedBy} on {new Date(config.lastModified).toLocaleDateString()}
                                  </div>
                                </div>
                                <div className="ml-4 min-w-[200px]">
                                  {config.type === 'boolean' ? (
                                    <Switch
                                      checked={currentValue}
                                      onCheckedChange={(checked) => updateConfig(config.id, checked)}
                                      disabled={config.isReadOnly}
                                    />
                                  ) : config.type === 'number' ? (
                                    <Input
                                      type="number"
                                      value={currentValue}
                                      onChange={(e) => updateConfig(config.id, parseInt(e.target.value))}
                                      min={config.validation?.min}
                                      max={config.validation?.max}
                                      disabled={config.isReadOnly}
                                    />
                                  ) : config.type === 'password' ? (
                                    <div className="flex gap-2">
                                      <Input
                                        type="password"
                                        value="••••••••"
                                        disabled
                                      />
                                      <Button variant="outline" size="sm">
                                        <Edit className="w-4 h-4" />
                                      </Button>
                                    </div>
                                  ) : config.validation?.options ? (
                                    <Select
                                      value={currentValue}
                                      onValueChange={(value) => updateConfig(config.id, value)}
                                      disabled={config.isReadOnly}
                                    >
                                      <SelectTrigger>
                                        <SelectValue />
                                      </SelectTrigger>
                                      <SelectContent>
                                        {config.validation.options.map((option) => (
                                          <SelectItem key={option} value={option}>
                                            {option}
                                          </SelectItem>
                                        ))}
                                      </SelectContent>
                                    </Select>
                                  ) : (
                                    <Input
                                      value={currentValue}
                                      onChange={(e) => updateConfig(config.id, e.target.value)}
                                      disabled={config.isReadOnly}
                                    />
                                  )}
                                </div>
                              </div>
                              {hasChanges && (
                                <div className="flex justify-end gap-2 mt-2">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                      const newChanges = { ...unsavedChanges }
                                      delete newChanges[config.id]
                                      setUnsavedChanges(newChanges)
                                    }}
                                  >
                                    <RotateCcw className="w-4 h-4 mr-1" />
                                    Revert
                                  </Button>
                                </div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>User Management</CardTitle>
                  <CardDescription>Manage user accounts, roles and permissions</CardDescription>
                </div>
                <Dialog open={showNewUserDialog} onOpenChange={setShowNewUserDialog}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      Add User
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Create New User</DialogTitle>
                      <DialogDescription>Add a new user to the system</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 mt-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>First Name</Label>
                          <Input placeholder="Enter first name" />
                        </div>
                        <div>
                          <Label>Last Name</Label>
                          <Input placeholder="Enter last name" />
                        </div>
                      </div>
                      <div>
                        <Label>Email Address</Label>
                        <Input type="email" placeholder="user@company.com" />
                      </div>
                      <div>
                        <Label>Username</Label>
                        <Input placeholder="Enter username" />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>Role</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select role" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="admin">System Admin</SelectItem>
                              <SelectItem value="bcm_manager">BCM Manager</SelectItem>
                              <SelectItem value="bcm_coordinator">BCM Coordinator</SelectItem>
                              <SelectItem value="user">User</SelectItem>
                              <SelectItem value="viewer">Viewer</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label>Department</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select department" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="it">Information Technology</SelectItem>
                              <SelectItem value="bcm">Business Continuity</SelectItem>
                              <SelectItem value="operations">Operations</SelectItem>
                              <SelectItem value="hr">Human Resources</SelectItem>
                              <SelectItem value="finance">Finance</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch id="active" defaultChecked />
                        <Label htmlFor="active">Active account</Label>
                      </div>
                      <div className="flex justify-end gap-2">
                        <Button variant="outline" onClick={() => setShowNewUserDialog(false)}>
                          Cancel
                        </Button>
                        <Button>
                          <Users className="w-4 h-4 mr-2" />
                          Create User
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.map((user: UserProfile) => (
                  <div key={user.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 font-medium">
                            {user.firstName[0]}{user.lastName[0]}
                          </span>
                        </div>
                        <div>
                          <div className="font-medium">{user.firstName} {user.lastName}</div>
                          <div className="text-sm text-muted-foreground">{user.email}</div>
                          <div className="text-xs text-muted-foreground">
                            {user.role} • {user.department}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {user.isActive ? (
                          <Badge className="bg-green-500">Active</Badge>
                        ) : (
                          <Badge className="bg-gray-500">Inactive</Badge>
                        )}
                        {user.twoFactorEnabled && (
                          <Badge variant="outline">2FA</Badge>
                        )}
                        <Badge variant="outline">
                          {user.permissions.includes('*') ? 'All Permissions' : `${user.permissions.length} Permissions`}
                        </Badge>
                      </div>
                    </div>
                    {user.lastLogin && (
                      <div className="text-xs text-muted-foreground mt-2">
                        Last login: {new Date(user.lastLogin).toLocaleString()}
                      </div>
                    )}
                    <div className="flex gap-2 mt-3">
                      <Button size="sm" variant="outline">
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                      <Button size="sm" variant="outline">
                        <Key className="w-4 h-4 mr-1" />
                        Reset Password
                      </Button>
                      <Button size="sm" variant="outline">
                        <Shield className="w-4 h-4 mr-1" />
                        Permissions
                      </Button>
                      {user.isActive ? (
                        <Button size="sm" variant="outline">
                          <XCircle className="w-4 h-4 mr-1" />
                          Deactivate
                        </Button>
                      ) : (
                        <Button size="sm" variant="outline">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Activate
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integrations" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>System Integrations</CardTitle>
              <CardDescription>Manage external system connections and APIs</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {integrations.map((integration: SystemIntegration) => (
                  <div key={integration.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium">{integration.name}</h3>
                          <Badge className={getStatusColor(integration.status)}>
                            {integration.status}
                          </Badge>
                          <Badge variant="outline" className="capitalize">
                            {integration.type.replace('_', ' ')}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{integration.description}</p>
                        {integration.endpoint && (
                          <div className="text-xs text-muted-foreground mt-1">
                            Endpoint: {integration.endpoint}
                          </div>
                        )}
                      </div>
                      <Switch
                        checked={integration.isEnabled}
                        disabled={integration.status === 'error'}
                      />
                    </div>
                    <div className="flex justify-between items-center text-xs text-muted-foreground">
                      <div>
                        {integration.lastSync && (
                          <span>Last sync: {new Date(integration.lastSync).toLocaleString()}</span>
                        )}
                      </div>
                      <div>
                        {integration.errorCount > 0 && (
                          <span className="text-red-600">
                            {integration.errorCount} error{integration.errorCount > 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2 mt-3">
                      <Button size="sm" variant="outline">
                        <Settings className="w-4 h-4 mr-1" />
                        Configure
                      </Button>
                      <Button size="sm" variant="outline">
                        <Activity className="w-4 h-4 mr-1" />
                        Test Connection
                      </Button>
                      <Button size="sm" variant="outline">
                        <RefreshCw className="w-4 h-4 mr-1" />
                        Sync Now
                      </Button>
                      {integration.errorCount > 0 && (
                        <Button size="sm" variant="outline">
                          <AlertTriangle className="w-4 h-4 mr-1" />
                          View Errors
                        </Button>
                      )}
                    </div>
                  </div>
                ))}

                {/* Add New Integration */}
                <div className="border-2 border-dashed rounded-lg p-6 text-center">
                  <Globe className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                  <h3 className="font-medium mb-1">Add New Integration</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    Connect with external systems and services
                  </p>
                  <Button variant="outline">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Integration
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="backup" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Backup & Recovery</CardTitle>
              <CardDescription>Manage data backup schedules and recovery options</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Backup Status Overview */}
                <div className="grid grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="p-4 text-center">
                      <HardDrive className="w-6 h-6 mx-auto mb-2 text-green-500" />
                      <div className="text-2xl font-bold">2.1 GB</div>
                      <div className="text-xs text-muted-foreground">Last backup size</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <Clock className="w-6 h-6 mx-auto mb-2 text-blue-500" />
                      <div className="text-2xl font-bold">98.5%</div>
                      <div className="text-xs text-muted-foreground">Success rate</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <Calendar className="w-6 h-6 mx-auto mb-2 text-purple-500" />
                      <div className="text-2xl font-bold">
                        {systemMetrics.lastBackup ?
                          Math.round((Date.now() - systemMetrics.lastBackup) / (1000 * 60 * 60)) + 'h'
                          : 'N/A'
                        }
                      </div>
                      <div className="text-xs text-muted-foreground">Hours since last backup</div>
                    </CardContent>
                  </Card>
                </div>

                {/* Backup Configurations */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Backup Configurations</h3>
                  {backups.map((backup: BackupConfig) => (
                    <div key={backup.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium">{backup.name}</h4>
                            <Badge className={getStatusColor(backup.status)}>
                              {backup.status}
                            </Badge>
                            <Badge variant="outline" className="capitalize">
                              {backup.type}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Schedule: {backup.schedule} • Retention: {backup.retention} days
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Destination: {backup.destination}
                          </div>
                        </div>
                        <Switch checked={backup.isEnabled} />
                      </div>
                      <div className="flex justify-between items-center text-xs text-muted-foreground mb-3">
                        <div>
                          Last backup: {backup.lastBackup ? new Date(backup.lastBackup).toLocaleString() : 'Never'}
                        </div>
                        <div>
                          Size: {backup.size ? formatFileSize(backup.size) : 'N/A'}
                        </div>
                        <div>
                          Next: {backup.nextBackup ? new Date(backup.nextBackup).toLocaleString() : 'N/A'}
                        </div>
                      </div>
                      <div className="flex items-center gap-4 text-xs">
                        <div className="flex items-center gap-1">
                          <Shield className="w-3 h-3" />
                          Encryption: {backup.encryption ? 'Enabled' : 'Disabled'}
                        </div>
                        <div className="flex items-center gap-1">
                          <Archive className="w-3 h-3" />
                          Compression: {backup.compression ? 'Enabled' : 'Disabled'}
                        </div>
                      </div>
                      <div className="flex gap-2 mt-3">
                        <Button size="sm" variant="outline">
                          <Play className="w-4 h-4 mr-1" />
                          Run Now
                        </Button>
                        <Button size="sm" variant="outline">
                          <Settings className="w-4 h-4 mr-1" />
                          Configure
                        </Button>
                        <Button size="sm" variant="outline">
                          <Download className="w-4 h-4 mr-1" />
                          Restore
                        </Button>
                        <Button size="sm" variant="outline">
                          <Eye className="w-4 h-4 mr-1" />
                          View Logs
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Audit Logs</CardTitle>
              <CardDescription>System activity and security audit trail</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Audit Summary */}
                <div className="grid grid-cols-4 gap-4">
                  <div className="border rounded p-3 text-center">
                    <div className="text-2xl font-bold text-blue-600">1,247</div>
                    <div className="text-xs text-muted-foreground">Total Events</div>
                  </div>
                  <div className="border rounded p-3 text-center">
                    <div className="text-2xl font-bold text-green-600">1,198</div>
                    <div className="text-xs text-muted-foreground">Successful</div>
                  </div>
                  <div className="border rounded p-3 text-center">
                    <div className="text-2xl font-bold text-yellow-600">35</div>
                    <div className="text-xs text-muted-foreground">Warnings</div>
                  </div>
                  <div className="border rounded p-3 text-center">
                    <div className="text-2xl font-bold text-red-600">14</div>
                    <div className="text-xs text-muted-foreground">Errors</div>
                  </div>
                </div>

                {/* Sample Audit Entries */}
                <div className="space-y-2">
                  <h4 className="font-medium">Recent Activity</h4>
                  <div className="border rounded-lg">
                    <table className="w-full text-sm">
                      <thead className="border-b bg-muted/50">
                        <tr>
                          <th className="text-left p-3">Timestamp</th>
                          <th className="text-left p-3">User</th>
                          <th className="text-left p-3">Action</th>
                          <th className="text-left p-3">Resource</th>
                          <th className="text-left p-3">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-b">
                          <td className="p-3">2024-01-15 10:30:15</td>
                          <td className="p-3">admin</td>
                          <td className="p-3">Configuration Updated</td>
                          <td className="p-3">system.session_timeout</td>
                          <td className="p-3">
                            <Badge className="bg-green-500">Success</Badge>
                          </td>
                        </tr>
                        <tr className="border-b">
                          <td className="p-3">2024-01-15 10:25:42</td>
                          <td className="p-3">bcm.manager</td>
                          <td className="p-3">User Login</td>
                          <td className="p-3">authentication</td>
                          <td className="p-3">
                            <Badge className="bg-green-500">Success</Badge>
                          </td>
                        </tr>
                        <tr className="border-b">
                          <td className="p-3">2024-01-15 10:20:18</td>
                          <td className="p-3">system</td>
                          <td className="p-3">Backup Completed</td>
                          <td className="p-3">backup.daily_full</td>
                          <td className="p-3">
                            <Badge className="bg-green-500">Success</Badge>
                          </td>
                        </tr>
                        <tr className="border-b">
                          <td className="p-3">2024-01-15 09:15:33</td>
                          <td className="p-3">api_user</td>
                          <td className="p-3">API Request Failed</td>
                          <td className="p-3">api.incidents.create</td>
                          <td className="p-3">
                            <Badge className="bg-red-500">Error</Badge>
                          </td>
                        </tr>
                        <tr>
                          <td className="p-3">2024-01-15 09:10:12</td>
                          <td className="p-3">admin</td>
                          <td className="p-3">Integration Enabled</td>
                          <td className="p-3">slack_notifications</td>
                          <td className="p-3">
                            <Badge className="bg-green-500">Success</Badge>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div className="flex justify-center">
                    <Button variant="outline">
                      <Eye className="w-4 h-4 mr-2" />
                      View All Logs
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}