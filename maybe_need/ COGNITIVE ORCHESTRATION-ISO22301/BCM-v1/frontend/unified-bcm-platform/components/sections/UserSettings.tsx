'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Settings, Bell, Shield, Eye, Palette } from 'lucide-react'

export function UserSettings() {
  const [settings, setSettings] = useState({
    // General Settings
    displayName: 'Sarah Johnson',
    email: 'sarah.johnson@company.com',
    timezone: 'UTC-05:00',
    language: 'en',
    
    // Notifications
    emailNotifications: true,
    pushNotifications: true,
    weeklyDigest: true,
    incidentAlerts: true,
    reviewReminders: true,
    exerciseNotifications: true,
    
    // Privacy
    profileVisibility: 'team',
    activityVisibility: 'team',
    shareProgress: true,
    
    // Appearance
    theme: 'system',
    compactMode: false,
    showProgressBars: true,
    
    // Dashboard
    defaultView: 'overview',
    refreshInterval: '30',
    showQuickActions: true,
    maxRecentItems: 10
  })

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">User Settings</h2>
          <p className="text-gray-600 mt-1">Manage your preferences and account settings</p>
        </div>
        <Button>Save Changes</Button>
      </div>

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="privacy">Privacy</TabsTrigger>
          <TabsTrigger value="appearance">Appearance</TabsTrigger>
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Update your personal information and preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="displayName">Display Name</Label>
                  <Input 
                    id="displayName"
                    value={settings.displayName}
                    onChange={(e) => handleSettingChange('displayName', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input 
                    id="email"
                    type="email"
                    value={settings.email}
                    onChange={(e) => handleSettingChange('email', e.target.value)}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select value={settings.timezone} onValueChange={(value) => handleSettingChange('timezone', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UTC-08:00">Pacific Time (UTC-8)</SelectItem>
                      <SelectItem value="UTC-07:00">Mountain Time (UTC-7)</SelectItem>
                      <SelectItem value="UTC-06:00">Central Time (UTC-6)</SelectItem>
                      <SelectItem value="UTC-05:00">Eastern Time (UTC-5)</SelectItem>
                      <SelectItem value="UTC+00:00">UTC (UTC+0)</SelectItem>
                      <SelectItem value="UTC+01:00">Central European Time (UTC+1)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="language">Language</Label>
                  <Select value={settings.language} onValueChange={(value) => handleSettingChange('language', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Spanish</SelectItem>
                      <SelectItem value="fr">French</SelectItem>
                      <SelectItem value="de">German</SelectItem>
                      <SelectItem value="ja">Japanese</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Account Security</CardTitle>
              <CardDescription>Manage your account security settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Two-Factor Authentication</div>
                  <div className="text-sm text-gray-600">Add an extra layer of security to your account</div>
                </div>
                <Button variant="outline">Configure</Button>
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Change Password</div>
                  <div className="text-sm text-gray-600">Update your account password</div>
                </div>
                <Button variant="outline">Change</Button>
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Active Sessions</div>
                  <div className="text-sm text-gray-600">Manage devices connected to your account</div>
                </div>
                <Button variant="outline">View Sessions</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                <CardTitle>Notification Preferences</CardTitle>
              </div>
              <CardDescription>Control how and when you receive notifications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Email Notifications</div>
                    <div className="text-sm text-gray-600">Receive notifications via email</div>
                  </div>
                  <Switch 
                    checked={settings.emailNotifications}
                    onCheckedChange={(checked) => handleSettingChange('emailNotifications', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Push Notifications</div>
                    <div className="text-sm text-gray-600">Receive push notifications in your browser</div>
                  </div>
                  <Switch 
                    checked={settings.pushNotifications}
                    onCheckedChange={(checked) => handleSettingChange('pushNotifications', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Weekly Digest</div>
                    <div className="text-sm text-gray-600">Receive a weekly summary of your BCM activities</div>
                  </div>
                  <Switch 
                    checked={settings.weeklyDigest}
                    onCheckedChange={(checked) => handleSettingChange('weeklyDigest', checked)}
                  />
                </div>
              </div>
              
              <Separator />
              
              <div>
                <h4 className="font-medium mb-4">Specific Notifications</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">Incident Alerts</div>
                      <div className="text-sm text-gray-600">Critical incident notifications</div>
                    </div>
                    <Switch 
                      checked={settings.incidentAlerts}
                      onCheckedChange={(checked) => handleSettingChange('incidentAlerts', checked)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">Review Reminders</div>
                      <div className="text-sm text-gray-600">Plan and document review reminders</div>
                    </div>
                    <Switch 
                      checked={settings.reviewReminders}
                      onCheckedChange={(checked) => handleSettingChange('reviewReminders', checked)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">Exercise Notifications</div>
                      <div className="text-sm text-gray-600">BCM exercise and drill notifications</div>
                    </div>
                    <Switch 
                      checked={settings.exerciseNotifications}
                      onCheckedChange={(checked) => handleSettingChange('exerciseNotifications', checked)}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="privacy" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                <CardTitle>Privacy Settings</CardTitle>
              </div>
              <CardDescription>Control who can see your information and activities</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="profileVisibility">Profile Visibility</Label>
                  <Select 
                    value={settings.profileVisibility} 
                    onValueChange={(value) => handleSettingChange('profileVisibility', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">Everyone</SelectItem>
                      <SelectItem value="organization">Organization</SelectItem>
                      <SelectItem value="team">Team Members Only</SelectItem>
                      <SelectItem value="private">Private</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="text-sm text-gray-600 mt-1">Who can see your profile information</div>
                </div>
                
                <div>
                  <Label htmlFor="activityVisibility">Activity Visibility</Label>
                  <Select 
                    value={settings.activityVisibility} 
                    onValueChange={(value) => handleSettingChange('activityVisibility', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">Everyone</SelectItem>
                      <SelectItem value="organization">Organization</SelectItem>
                      <SelectItem value="team">Team Members Only</SelectItem>
                      <SelectItem value="private">Private</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="text-sm text-gray-600 mt-1">Who can see your BCM activities</div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Share Progress</div>
                    <div className="text-sm text-gray-600">Allow others to see your task completion progress</div>
                  </div>
                  <Switch 
                    checked={settings.shareProgress}
                    onCheckedChange={(checked) => handleSettingChange('shareProgress', checked)}
                  />
                </div>
              </div>
              
              <Separator />
              
              <div className="space-y-4">
                <h4 className="font-medium">Data Management</h4>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start">
                    Export My Data
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    Download Activity Report
                  </Button>
                  <Button variant="destructive" className="w-full justify-start">
                    Delete Account
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="appearance" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                <CardTitle>Appearance</CardTitle>
              </div>
              <CardDescription>Customize the look and feel of your dashboard</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="theme">Theme</Label>
                  <Select value={settings.theme} onValueChange={(value) => handleSettingChange('theme', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="system">System</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="text-sm text-gray-600 mt-1">Choose your preferred theme</div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Compact Mode</div>
                    <div className="text-sm text-gray-600">Reduce spacing and padding for more content</div>
                  </div>
                  <Switch 
                    checked={settings.compactMode}
                    onCheckedChange={(checked) => handleSettingChange('compactMode', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Show Progress Bars</div>
                    <div className="text-sm text-gray-600">Display progress bars for tasks and metrics</div>
                  </div>
                  <Switch 
                    checked={settings.showProgressBars}
                    onCheckedChange={(checked) => handleSettingChange('showProgressBars', checked)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dashboard" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                <CardTitle>Dashboard Preferences</CardTitle>
              </div>
              <CardDescription>Customize your dashboard layout and behavior</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="defaultView">Default View</Label>
                  <Select 
                    value={settings.defaultView} 
                    onValueChange={(value) => handleSettingChange('defaultView', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="overview">Overview</SelectItem>
                      <SelectItem value="tasks">My Tasks</SelectItem>
                      <SelectItem value="metrics">Performance</SelectItem>
                      <SelectItem value="calendar">Calendar</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="text-sm text-gray-600 mt-1">Default tab when opening your dashboard</div>
                </div>
                
                <div>
                  <Label htmlFor="refreshInterval">Auto-refresh Interval</Label>
                  <Select 
                    value={settings.refreshInterval} 
                    onValueChange={(value) => handleSettingChange('refreshInterval', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="15">15 seconds</SelectItem>
                      <SelectItem value="30">30 seconds</SelectItem>
                      <SelectItem value="60">1 minute</SelectItem>
                      <SelectItem value="300">5 minutes</SelectItem>
                      <SelectItem value="0">Disabled</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="text-sm text-gray-600 mt-1">How often to refresh dashboard data</div>
                </div>
                
                <div>
                  <Label htmlFor="maxRecentItems">Recent Items Limit</Label>
                  <Select 
                    value={settings.maxRecentItems.toString()} 
                    onValueChange={(value) => handleSettingChange('maxRecentItems', parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="5">5 items</SelectItem>
                      <SelectItem value="10">10 items</SelectItem>
                      <SelectItem value="15">15 items</SelectItem>
                      <SelectItem value="20">20 items</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="text-sm text-gray-600 mt-1">Number of recent items to show</div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Show Quick Actions</div>
                    <div className="text-sm text-gray-600">Display quick action buttons in dashboard</div>
                  </div>
                  <Switch 
                    checked={settings.showQuickActions}
                    onCheckedChange={(checked) => handleSettingChange('showQuickActions', checked)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}