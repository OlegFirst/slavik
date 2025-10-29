'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import {
  User,
  Settings,
  Shield,
  Bell,
  Building,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Activity,
  LogOut,
  Edit,
  Save,
  X
} from 'lucide-react'
import { useAuth } from '@/components/auth/AuthProvider'
import { unifiedApi } from '@/lib/api/unified-api-client'

export function UserProfile() {
  const { user, logout } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [editedProfile, setEditedProfile] = useState({
    firstName: user?.firstName || '',
    lastName: user?.lastName || '',
    email: user?.email || '',
    phone: '',
    department: user?.departments?.[0] || '',
    location: ''
  })

  const [preferences, setPreferences] = useState({
    emailNotifications: true,
    pushNotifications: true,
    weeklyReports: true,
    securityAlerts: true,
    darkMode: false,
    language: 'en'
  })

  if (!user) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Not Authenticated</h3>
          <p className="text-gray-600">Please log in to view your profile.</p>
        </div>
      </div>
    )
  }

  const handleSaveProfile = async () => {
    try {
      // Update profile via API
      await unifiedApi.odoo('res.users', 'write', [[user.odooUserId], {
        name: `${editedProfile.firstName} ${editedProfile.lastName}`,
        email: editedProfile.email,
        phone: editedProfile.phone,
        // department_id: editedProfile.department
      }])

      setIsEditing(false)
      // TODO: Refresh user data
    } catch (error) {
      console.error('Failed to update profile:', error)
    }
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'super_admin': return 'bg-red-100 text-red-800'
      case 'org_admin': return 'bg-purple-100 text-purple-800'
      case 'manager': return 'bg-blue-100 text-blue-800'
      case 'analyst': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Profile Header */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-6">
            <Avatar className="h-24 w-24">
              <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${user.firstName}${user.lastName}`} />
              <AvatarFallback className="text-2xl">
                {user.firstName[0]}{user.lastName[0]}
              </AvatarFallback>
            </Avatar>

            <div className="flex-1">
              <div className="flex items-center space-x-4 mb-2">
                <h1 className="text-2xl font-bold text-gray-900">
                  {user.firstName} {user.lastName}
                </h1>
                <Badge className={getRoleBadgeColor(user.role)}>
                  {user.role.replace('_', ' ').toUpperCase()}
                </Badge>
              </div>

              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="flex items-center space-x-1">
                  <Mail className="h-4 w-4" />
                  <span>{user.email}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Building className="h-4 w-4" />
                  <span>{user.companyName}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Calendar className="h-4 w-4" />
                  <span>Member since {new Date().getFullYear()}</span>
                </div>
              </div>

              <div className="flex items-center space-x-2 mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsEditing(!isEditing)}
                >
                  <Edit className="h-4 w-4 mr-2" />
                  {isEditing ? 'Cancel' : 'Edit Profile'}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={logout}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Profile Tabs */}
      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="h-5 w-5" />
                <span>Personal Information</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    value={isEditing ? editedProfile.firstName : user.firstName}
                    onChange={(e) => setEditedProfile(prev => ({ ...prev, firstName: e.target.value }))}
                    disabled={!isEditing}
                  />
                </div>
                <div>
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    value={isEditing ? editedProfile.lastName : user.lastName}
                    onChange={(e) => setEditedProfile(prev => ({ ...prev, lastName: e.target.value }))}
                    disabled={!isEditing}
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={isEditing ? editedProfile.email : user.email}
                    onChange={(e) => setEditedProfile(prev => ({ ...prev, email: e.target.value }))}
                    disabled={!isEditing}
                  />
                </div>
                <div>
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    value={editedProfile.phone}
                    onChange={(e) => setEditedProfile(prev => ({ ...prev, phone: e.target.value }))}
                    disabled={!isEditing}
                    placeholder="Not set"
                  />
                </div>
                <div>
                  <Label htmlFor="department">Department</Label>
                  <Input
                    id="department"
                    value={isEditing ? editedProfile.department : user.departments?.[0] || 'Not assigned'}
                    onChange={(e) => setEditedProfile(prev => ({ ...prev, department: e.target.value }))}
                    disabled={!isEditing}
                  />
                </div>
                <div>
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    value={editedProfile.location}
                    onChange={(e) => setEditedProfile(prev => ({ ...prev, location: e.target.value }))}
                    disabled={!isEditing}
                    placeholder="Not set"
                  />
                </div>
              </div>

              {isEditing && (
                <div className="flex space-x-2">
                  <Button onClick={handleSaveProfile}>
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
                  <Button variant="outline" onClick={() => setIsEditing(false)}>
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Company Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Building className="h-5 w-5" />
                <span>Organization Information</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label>Company Name</Label>
                  <div className="text-sm font-medium">{user.companyName}</div>
                </div>
                <div>
                  <Label>Company ID</Label>
                  <div className="text-sm font-medium">#{user.companyId}</div>
                </div>
                <div>
                  <Label>User Role</Label>
                  <Badge className={getRoleBadgeColor(user.role)}>
                    {user.role.replace('_', ' ').toUpperCase()}
                  </Badge>
                </div>
                <div>
                  <Label>Departments</Label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {user.departments.map((dept, index) => (
                      <Badge key={index} variant="outline">{dept}</Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Security & Authentication</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4">Session Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Session ID</Label>
                    <div className="text-sm font-mono bg-gray-50 p-2 rounded">
                      {user.sessionId}
                    </div>
                  </div>
                  <div>
                    <Label>Session Expires</Label>
                    <div className="text-sm">
                      {user.expiresAt.toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-lg font-medium mb-4">Permissions</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {user.permissions.map((permission, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {permission}
                    </Badge>
                  ))}
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-lg font-medium mb-4">BCM Modules Access</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {user.modules.map((module, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {module}
                    </Badge>
                  ))}
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h3 className="text-lg font-medium">Security Actions</h3>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start">
                    Change Password
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    Two-Factor Authentication
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    Active Sessions
                  </Button>
                  <Button variant="destructive" className="w-full justify-start">
                    Revoke All Sessions
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Preferences Tab */}
        <TabsContent value="preferences">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>Preferences & Settings</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4">Notifications</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Email Notifications</Label>
                      <p className="text-sm text-gray-600">Receive updates via email</p>
                    </div>
                    <Switch
                      checked={preferences.emailNotifications}
                      onCheckedChange={(checked) =>
                        setPreferences(prev => ({ ...prev, emailNotifications: checked }))
                      }
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Push Notifications</Label>
                      <p className="text-sm text-gray-600">Browser notifications</p>
                    </div>
                    <Switch
                      checked={preferences.pushNotifications}
                      onCheckedChange={(checked) =>
                        setPreferences(prev => ({ ...prev, pushNotifications: checked }))
                      }
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Weekly Reports</Label>
                      <p className="text-sm text-gray-600">Get weekly summary reports</p>
                    </div>
                    <Switch
                      checked={preferences.weeklyReports}
                      onCheckedChange={(checked) =>
                        setPreferences(prev => ({ ...prev, weeklyReports: checked }))
                      }
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Security Alerts</Label>
                      <p className="text-sm text-gray-600">Important security notifications</p>
                    </div>
                    <Switch
                      checked={preferences.securityAlerts}
                      onCheckedChange={(checked) =>
                        setPreferences(prev => ({ ...prev, securityAlerts: checked }))
                      }
                    />
                  </div>
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-lg font-medium mb-4">Interface</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Dark Mode</Label>
                      <p className="text-sm text-gray-600">Use dark theme</p>
                    </div>
                    <Switch
                      checked={preferences.darkMode}
                      onCheckedChange={(checked) =>
                        setPreferences(prev => ({ ...prev, darkMode: checked }))
                      }
                    />
                  </div>
                  <div>
                    <Label htmlFor="language">Language</Label>
                    <Input
                      id="language"
                      value={preferences.language}
                      disabled
                      className="w-full md:w-48"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <Button>Save Preferences</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Activity Tab */}
        <TabsContent value="activity">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Recent Activity</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border-l-2 border-blue-500 pl-4">
                  <div className="text-sm font-medium">Logged in from new device</div>
                  <div className="text-xs text-gray-600">2 hours ago</div>
                </div>
                <div className="border-l-2 border-green-500 pl-4">
                  <div className="text-sm font-medium">Updated BIA assessment</div>
                  <div className="text-xs text-gray-600">1 day ago</div>
                </div>
                <div className="border-l-2 border-yellow-500 pl-4">
                  <div className="text-sm font-medium">Completed security training</div>
                  <div className="text-xs text-gray-600">3 days ago</div>
                </div>
                <div className="border-l-2 border-purple-500 pl-4">
                  <div className="text-sm font-medium">Created new incident response plan</div>
                  <div className="text-xs text-gray-600">1 week ago</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}