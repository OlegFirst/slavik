import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import {
  Users,
  UserPlus,
  Search,
  Filter,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Info,
  ExternalLink,
  Edit3,
  Eye,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Shield,
  UserCheck,
  Activity,
  Clock,
  Ban,
  CheckSquare,
  Globe,
  Settings,
  Key
} from 'lucide-react';
import { userService, User, UserMetrics } from '@/services/users';

const UserManager: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [metrics, setMetrics] = useState<UserMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: '',
    email: '',
    username: '',
    role: 'viewer' as User['role'],
    department: '',
    status: 'active' as User['status'],
    phone: '',
    location: '',
    language: 'en_US',
    timezone: 'UTC',
    two_factor_enabled: false,
    permissions: ['read'],
    bcm_modules_access: [] as string[],
    client_access: [] as string[]
  });

  useEffect(() => {
    loadUsers();
    loadMetrics();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      console.log('👤 Loading users from Odoo...');
      const usersData = await userService.getAdminUsers();
      setUsers(usersData);
      console.log('✅ Users loaded:', usersData.length);
    } catch (error) {
      console.error('❌ Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      const metricsData = await userService.getUserMetrics();
      setMetrics(metricsData);
    } catch (error) {
      console.error('❌ Failed to load metrics:', error);
    }
  };

  const handleCreateUser = async () => {
    if (!createForm.name || !createForm.email || !createForm.username) return;

    setCreating(true);
    try {
      const userData = {
        ...createForm,
        bcm_modules_access: createForm.bcm_modules_access,
        client_access: createForm.client_access
      };

      console.log('➕ Creating new user...');
      const success = await userService.createUser(userData);

      if (success) {
        console.log('✅ User created successfully');
        await loadUsers();
        await loadMetrics();
        setCreateDialogOpen(false);
        setCreateForm({
          name: '',
          email: '',
          username: '',
          role: 'viewer',
          department: '',
          status: 'active',
          phone: '',
          location: '',
          language: 'en_US',
          timezone: 'UTC',
          two_factor_enabled: false,
          permissions: ['read'],
          bcm_modules_access: [],
          client_access: []
        });
      } else {
        console.error('❌ User creation failed');
      }
    } catch (error) {
      console.error('❌ Create error:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleToggleUserStatus = async (userId: string, currentStatus: User['status']) => {
    const newStatus = currentStatus === 'active' ? 'suspended' : 'active';

    try {
      const success = await userService.toggleUserStatus(userId, newStatus);
      if (success) {
        console.log(`✅ User status changed to ${newStatus}`);
        await loadUsers();
        await loadMetrics();
      }
    } catch (error) {
      console.error('❌ Failed to toggle user status:', error);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesRole = selectedRole === 'all' || user.role === selectedRole;
    const matchesStatus = selectedStatus === 'all' || user.status === selectedStatus;
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.department.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesRole && matchesStatus && matchesSearch;
  });

  const getRoleColor = (role: User['role']) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'manager': return 'bg-blue-100 text-blue-800';
      case 'analyst': return 'bg-purple-100 text-purple-800';
      case 'viewer': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: User['status']) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'suspended': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderUserCard = (user: User) => (
    <Card key={user.id} className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg flex items-center gap-2">
              <UserCheck className="h-5 w-5 text-blue-600" />
              {user.name}
            </CardTitle>
            <div className="flex items-center gap-2 mt-2">
              <Badge className={getRoleColor(user.role)}>
                {user.role}
              </Badge>
              <Badge className={getStatusColor(user.status)}>
                {user.status}
              </Badge>
              {user.two_factor_enabled && (
                <Badge variant="outline" className="text-xs">
                  <Shield className="h-3 w-3 mr-1" />
                  2FA
                </Badge>
              )}
            </div>
          </div>
          <div className="flex items-center gap-1">
            <Button size="sm" variant="ghost">
              <Eye className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="ghost">
              <Edit3 className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleToggleUserStatus(user.id, user.status)}
              className={user.status === 'suspended' ? 'text-green-600' : 'text-red-600'}
            >
              {user.status === 'suspended' ? <CheckCircle className="h-4 w-4" /> : <Ban className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm">
            <Mail className="h-4 w-4 text-muted-foreground" />
            <span>{user.email}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <UserCheck className="h-4 w-4 text-muted-foreground" />
            <span>@{user.username}</span>
          </div>
          {user.phone && (
            <div className="flex items-center gap-2 text-sm">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <span>{user.phone}</span>
            </div>
          )}
          <div className="flex items-center gap-2 text-sm">
            <Settings className="h-4 w-4 text-muted-foreground" />
            <span>{user.department}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mt-4 pt-3 border-t text-sm">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-muted-foreground" />
            <span>{user.login_count} logins</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span>{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</span>
          </div>
          <div className="flex items-center gap-2">
            <Key className="h-4 w-4 text-muted-foreground" />
            <span>{user.permissions.length} permissions</span>
          </div>
          <div className="flex items-center gap-2">
            <Globe className="h-4 w-4 text-muted-foreground" />
            <span>{user.timezone}</span>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t">
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <CheckSquare className="h-3 w-3" />
            <span>Modules: {user.bcm_modules_access.length || 'None'}</span>
            <span className="mx-2">•</span>
            <span>Clients: {user.client_access.length || 'None'}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-lg">Loading users from Odoo...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Metrics Overview */}
      {metrics && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Users className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">Total Users</p>
                  <p className="text-2xl font-bold">{metrics.total_users}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <CheckCircle className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">Active</p>
                  <p className="text-2xl font-bold">{metrics.active_users}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <UserPlus className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">New This Month</p>
                  <p className="text-2xl font-bold">{metrics.new_users_this_month}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Activity className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">Recent Logins</p>
                  <p className="text-2xl font-bold">{metrics.recent_logins}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Header with actions */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">BCM User Management</h3>
          <p className="text-sm text-muted-foreground">
            Manage user accounts, roles, and permissions - integrated with Odoo user management
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <UserPlus className="h-4 w-4 mr-2" />
                Add User
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create New User</DialogTitle>
              </DialogHeader>
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Full Name</Label>
                    <Input
                      value={createForm.name}
                      onChange={(e) => setCreateForm(prev => ({...prev, name: e.target.value}))}
                      placeholder="John Doe"
                    />
                  </div>
                  <div>
                    <Label>Username</Label>
                    <Input
                      value={createForm.username}
                      onChange={(e) => setCreateForm(prev => ({...prev, username: e.target.value}))}
                      placeholder="jdoe"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Email</Label>
                    <Input
                      type="email"
                      value={createForm.email}
                      onChange={(e) => setCreateForm(prev => ({...prev, email: e.target.value}))}
                      placeholder="john.doe@company.com"
                    />
                  </div>
                  <div>
                    <Label>Phone</Label>
                    <Input
                      value={createForm.phone}
                      onChange={(e) => setCreateForm(prev => ({...prev, phone: e.target.value}))}
                      placeholder="+1-555-0123"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label>Role</Label>
                    <Select
                      value={createForm.role}
                      onValueChange={(value: User['role']) => setCreateForm(prev => ({...prev, role: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="viewer">Viewer</SelectItem>
                        <SelectItem value="analyst">Analyst</SelectItem>
                        <SelectItem value="manager">Manager</SelectItem>
                        <SelectItem value="admin">Admin</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Department</Label>
                    <Input
                      value={createForm.department}
                      onChange={(e) => setCreateForm(prev => ({...prev, department: e.target.value}))}
                      placeholder="e.g., Operations"
                    />
                  </div>
                  <div>
                    <Label>Location</Label>
                    <Input
                      value={createForm.location}
                      onChange={(e) => setCreateForm(prev => ({...prev, location: e.target.value}))}
                      placeholder="e.g., HQ Office"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Language</Label>
                    <Select
                      value={createForm.language}
                      onValueChange={(value) => setCreateForm(prev => ({...prev, language: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en_US">English (US)</SelectItem>
                        <SelectItem value="en_GB">English (UK)</SelectItem>
                        <SelectItem value="es_ES">Spanish</SelectItem>
                        <SelectItem value="fr_FR">French</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Timezone</Label>
                    <Select
                      value={createForm.timezone}
                      onValueChange={(value) => setCreateForm(prev => ({...prev, timezone: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="UTC">UTC</SelectItem>
                        <SelectItem value="America/New_York">Eastern Time</SelectItem>
                        <SelectItem value="America/Chicago">Central Time</SelectItem>
                        <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={createForm.two_factor_enabled}
                    onCheckedChange={(checked) => setCreateForm(prev => ({...prev, two_factor_enabled: checked}))}
                  />
                  <Label>Enable Two-Factor Authentication</Label>
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setCreateDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleCreateUser}
                    disabled={creating || !createForm.name || !createForm.email || !createForm.username}
                  >
                    {creating ? (
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <UserPlus className="h-4 w-4 mr-2" />
                    )}
                    Create User
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          <Button variant="outline" onClick={loadUsers}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search users by name, email, or department..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Select value={selectedRole} onValueChange={setSelectedRole}>
          <SelectTrigger className="w-32">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Roles</SelectItem>
            <SelectItem value="admin">Admin</SelectItem>
            <SelectItem value="manager">Manager</SelectItem>
            <SelectItem value="analyst">Analyst</SelectItem>
            <SelectItem value="viewer">Viewer</SelectItem>
          </SelectContent>
        </Select>
        <Select value={selectedStatus} onValueChange={setSelectedStatus}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
            <SelectItem value="suspended">Suspended</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Users Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredUsers.map(renderUserCard)}
      </div>

      {filteredUsers.length === 0 && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            No users found matching your criteria. Try adjusting the search or filters.
          </AlertDescription>
        </Alert>
      )}

      {/* Integration Status */}
      <Alert>
        <CheckCircle className="h-4 w-4" />
        <AlertTitle>Odoo BCM User Integration</AlertTitle>
        <AlertDescription>
          User accounts are synchronized with Odoo res.users with BCM-specific fields and permissions.
          Role-based access control is enforced across all BCM modules and client data.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default UserManager;