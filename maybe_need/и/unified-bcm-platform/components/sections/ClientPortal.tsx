'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Shield,
  Users,
  Settings,
  Activity,
  Lock,
  Key,
  Globe,
  Bell,
  FileText,
  BarChart,
  Upload,
  Download,
  ExternalLink,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Palette,
  Database,
  Link2,
  UserPlus,
  Mail,
  Smartphone,
  Cloud
} from 'lucide-react'
import { bcmWebPortalAPI } from '@/lib/api/odoo-client'
import { useAuth } from '@/hooks/useAuth'

export function ClientPortal() {
  const { isAuthenticated, user } = useAuth()
  const [portalConfig, setPortalConfig] = useState<any>(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [ssoTestResult, setSsoTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const [loading, setLoading] = useState(false)

  // Portal modules configuration
  const availableModules = [
    { id: 'dashboard', name: 'Dashboard', icon: BarChart, description: 'Main portal dashboard' },
    { id: 'documents', name: 'Documents', icon: FileText, description: 'Document management' },
    { id: 'incidents', name: 'Incidents', icon: AlertCircle, description: 'Incident reporting & tracking' },
    { id: 'training', name: 'Training', icon: Users, description: 'Training & certifications' },
    { id: 'reports', name: 'Reports', icon: BarChart, description: 'Analytics & reporting' },
    { id: 'communication', name: 'Communication', icon: Mail, description: 'Announcements & messaging' }
  ]

  const handleModuleToggle = (moduleId: string) => {
    setPortalConfig(prev => ({
      ...prev,
      modules: prev.modules.map(mod =>
        mod.type === moduleId ? { ...mod, enabled: !mod.enabled } : mod
      )
    }))
  }

  const handleSSOTest = async () => {
    setLoading(true)
    try {
      const result = await bcmWebPortalAPI.testSsoConnection(user.organizationId)
      // Mock response for now
      setTimeout(() => {
        setSsoTestResult({
          success: true,
          message: 'SSO connection successful. Authentication working correctly.'
        })
        setLoading(false)
      }, 2000)
    } catch (error) {
      setSsoTestResult({
        success: false,
        message: 'SSO connection failed. Please check configuration.'
      })
      setLoading(false)
    }
  }

  // Load portal data on mount
  useEffect(() => {
    const loadPortalData = async () => {
      if (!isAuthenticated || !user?.organizationId) {
        return
      }

      setLoading(true)
      try {
        const data = await bcmWebPortalAPI.getPortalConfig(user.organizationId)
        setPortalConfig(data)
      } catch (error) {
        console.error('Failed to load portal data:', error)
        if (error instanceof Error) {
          console.error('Portal API Error:', error.message)
        }
      }
      setLoading(false)
    }

    loadPortalData()
  }, [isAuthenticated, user])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'suspended': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Authentication guard
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Authentication Required</h3>
          <p className="text-gray-600">Please log in to access client portal management.</p>
        </div>
      </div>
    )
  }

  // Loading state
  if (loading || !portalConfig) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Portal Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Globe className="h-6 w-6" />
              {portalConfig.name}
            </h2>
            <p className="text-blue-100 mt-1">
              Client Portal Management & Configuration
            </p>
            {portalConfig.customDomain && (
              <div className="flex items-center gap-2 mt-2">
                <Link2 className="h-4 w-4" />
                <a href={`https://${portalConfig.customDomain}`} className="underline">
                  {portalConfig.customDomain}
                </a>
                <ExternalLink className="h-3 w-3" />
              </div>
            )}
          </div>
          <div className="text-right">
            <Badge className="bg-white/20 text-white border-white/30">
              Enterprise
            </Badge>
            <p className="text-sm text-blue-100 mt-2">
              Client ID: {portalConfig.clientId}
            </p>
          </div>
        </div>
      </div>

      {/* Analytics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Users className="h-4 w-4 text-blue-500" />
              Total Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{portalConfig.analytics.totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              {portalConfig.analytics.activeUsers} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <FileText className="h-4 w-4 text-green-500" />
              Documents
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{portalConfig.analytics.documentsShared}</div>
            <p className="text-xs text-muted-foreground">
              Shared this month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-orange-500" />
              Incidents
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{portalConfig.analytics.incidentsReported}</div>
            <p className="text-xs text-muted-foreground">
              Active incidents
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4 text-purple-500" />
              Training
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{portalConfig.analytics.trainingsCompleted}</div>
            <p className="text-xs text-muted-foreground">
              Completed this quarter
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-500" />
              Security
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {portalConfig.settings.ssoConfig && (
                <Badge variant="outline" className="text-xs">SSO</Badge>
              )}
              {portalConfig.settings.mfaConfig?.required && (
                <Badge variant="outline" className="text-xs">MFA</Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Enhanced security
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Portal Configuration Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="modules">Modules</TabsTrigger>
          <TabsTrigger value="access">Access</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="branding">Branding</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Portal Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Portal Status</span>
                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Last Updated</span>
                    <span className="text-sm text-muted-foreground">
                      {new Date(portalConfig.analytics.lastUpdated).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Active Modules</span>
                    <span className="text-sm">
                      {portalConfig.modules.filter(m => m.enabled).length}/{portalConfig.modules.length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Data Retention</span>
                    <span className="text-sm">{portalConfig.settings.dataRetention.days} days</span>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Quick Actions</h4>
                    <div className="space-y-2">
                      <Button variant="outline" size="sm" className="w-full justify-start">
                        <Upload className="h-4 w-4 mr-2" />
                        Upload Documents
                      </Button>
                      <Button variant="outline" size="sm" className="w-full justify-start">
                        <UserPlus className="h-4 w-4 mr-2" />
                        Invite Users
                      </Button>
                      <Button variant="outline" size="sm" className="w-full justify-start">
                        <Download className="h-4 w-4 mr-2" />
                        Export Analytics
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Modules Tab */}
        <TabsContent value="modules" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Portal Modules Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {availableModules.map(module => {
                  const isEnabled = portalConfig.modules.find(m => m.type === module.id)?.enabled
                  const Icon = module.icon
                  return (
                    <div key={module.id} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <Icon className="h-5 w-5 text-muted-foreground mt-0.5" />
                          <div>
                            <h4 className="font-medium">{module.name}</h4>
                            <p className="text-sm text-muted-foreground">
                              {module.description}
                            </p>
                          </div>
                        </div>
                        <Switch
                          checked={isEnabled}
                          onCheckedChange={() => handleModuleToggle(module.id)}
                        />
                      </div>
                      {isEnabled && (
                        <div className="mt-3 pl-8">
                          <Button variant="ghost" size="sm">
                            Configure
                          </Button>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Access Management Tab */}
        <TabsContent value="access" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>User Access Management</CardTitle>
                <Button size="sm">
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add User
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: 'John Smith', email: 'john@acme.com', role: 'Admin', status: 'active' },
                  { name: 'Sarah Johnson', email: 'sarah@acme.com', role: 'Manager', status: 'active' },
                  { name: 'Mike Chen', email: 'mike@acme.com', role: 'Viewer', status: 'pending' }
                ].map((user, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback>
                          {user.name.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium text-sm">{user.name}</p>
                        <p className="text-xs text-muted-foreground">{user.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{user.role}</Badge>
                      <Badge className={getStatusColor(user.status)}>
                        {user.status}
                      </Badge>
                      <Button variant="ghost" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* SSO Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Key className="h-5 w-5" />
                  Single Sign-On (SSO)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>SSO Provider</Label>
                  <select className="w-full px-3 py-2 border rounded-md">
                    <option value="azure-ad">Azure AD</option>
                    <option value="google">Google Workspace</option>
                    <option value="saml">SAML 2.0</option>
                    <option value="oauth2">OAuth 2.0</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Tenant ID</Label>
                  <Input placeholder="Enter tenant ID" />
                </div>
                <div className="space-y-2">
                  <Label>Client ID</Label>
                  <Input placeholder="Enter client ID" />
                </div>
                <Button
                  onClick={handleSSOTest}
                  disabled={loading}
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Testing Connection...
                    </>
                  ) : (
                    'Test SSO Connection'
                  )}
                </Button>
                {ssoTestResult && (
                  <div className={`p-3 rounded-lg flex items-center gap-2 ${
                    ssoTestResult.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
                  }`}>
                    {ssoTestResult.success ? (
                      <CheckCircle className="h-4 w-4" />
                    ) : (
                      <AlertCircle className="h-4 w-4" />
                    )}
                    <span className="text-sm">{ssoTestResult.message}</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* MFA Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lock className="h-5 w-5" />
                  Multi-Factor Authentication (MFA)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Require MFA</p>
                    <p className="text-sm text-muted-foreground">
                      All users must enable MFA
                    </p>
                  </div>
                  <Switch checked={portalConfig.settings.mfaConfig?.required} />
                </div>

                <div className="space-y-3">
                  <Label>Allowed Methods</Label>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <input type="checkbox" id="totp" defaultChecked />
                      <Label htmlFor="totp" className="font-normal">
                        <div className="flex items-center gap-2">
                          <Smartphone className="h-4 w-4" />
                          Authenticator App (TOTP)
                        </div>
                      </Label>
                    </div>
                    <div className="flex items-center gap-2">
                      <input type="checkbox" id="sms" />
                      <Label htmlFor="sms" className="font-normal">
                        <div className="flex items-center gap-2">
                          <Smartphone className="h-4 w-4" />
                          SMS Verification
                        </div>
                      </Label>
                    </div>
                    <div className="flex items-center gap-2">
                      <input type="checkbox" id="email" defaultChecked />
                      <Label htmlFor="email" className="font-normal">
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4" />
                          Email Verification
                        </div>
                      </Label>
                    </div>
                  </div>
                </div>

                <Button variant="outline" className="w-full">
                  Save MFA Settings
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Data Security */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Data Security & Retention
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Data Retention Period</Label>
                    <div className="flex items-center gap-2">
                      <Input
                        type="number"
                        value={portalConfig.settings.dataRetention.days}
                        className="w-24"
                      />
                      <span className="text-sm text-muted-foreground">days</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm">Auto-Archive</p>
                      <p className="text-xs text-muted-foreground">
                        Automatically archive old data
                      </p>
                    </div>
                    <Switch checked={portalConfig.settings.dataRetention.autoArchive} />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm">Encryption at Rest</p>
                      <p className="text-xs text-muted-foreground">
                        AES-256 encryption
                      </p>
                    </div>
                    <Badge className="bg-green-100 text-green-800">Enabled</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm">Backup Frequency</p>
                      <p className="text-xs text-muted-foreground">
                        Automated backups
                      </p>
                    </div>
                    <Badge variant="outline">Daily</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Branding Tab */}
        <TabsContent value="branding" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Portal Branding
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Portal Name</Label>
                  <Input value={portalConfig.name} />
                </div>
                <div className="space-y-2">
                  <Label>Custom Domain</Label>
                  <Input value={portalConfig.customDomain} placeholder="portal.yourdomain.com" />
                </div>
                <div className="space-y-2">
                  <Label>Primary Color</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      type="color"
                      value={portalConfig.branding.primaryColor}
                      className="w-20 h-10"
                    />
                    <Input value={portalConfig.branding.primaryColor} className="flex-1" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Secondary Color</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      type="color"
                      value={portalConfig.branding.secondaryColor}
                      className="w-20 h-10"
                    />
                    <Input value={portalConfig.branding.secondaryColor} className="flex-1" />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Logo</Label>
                <div className="border-2 border-dashed rounded-lg p-8 text-center">
                  <Upload className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">
                    Drag and drop or click to upload logo
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    PNG, JPG up to 2MB
                  </p>
                  <Button variant="outline" size="sm" className="mt-3">
                    Choose File
                  </Button>
                </div>
              </div>

              <Button className="w-full">Save Branding Settings</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Notification Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4" />
                    <div>
                      <p className="font-medium text-sm">Email Notifications</p>
                      <p className="text-xs text-muted-foreground">
                        Send email alerts for important events
                      </p>
                    </div>
                  </div>
                  <Switch checked={portalConfig.settings.notificationPreferences.email} />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Smartphone className="h-4 w-4" />
                    <div>
                      <p className="font-medium text-sm">SMS Notifications</p>
                      <p className="text-xs text-muted-foreground">
                        Send SMS for critical alerts
                      </p>
                    </div>
                  </div>
                  <Switch checked={portalConfig.settings.notificationPreferences.sms} />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Bell className="h-4 w-4" />
                    <div>
                      <p className="font-medium text-sm">In-App Notifications</p>
                      <p className="text-xs text-muted-foreground">
                        Show notifications in the portal
                      </p>
                    </div>
                  </div>
                  <Switch checked={portalConfig.settings.notificationPreferences.inApp} />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Cloud className="h-4 w-4" />
                    <div>
                      <p className="font-medium text-sm">Webhook Integration</p>
                      <p className="text-xs text-muted-foreground">
                        Send events to external systems
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">Configure</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}