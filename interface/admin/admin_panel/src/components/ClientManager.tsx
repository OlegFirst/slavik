import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import {
  Users,
  Plus,
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
  Building,
  MapPin,
  TrendingUp,
  Calendar,
  Shield,
  DollarSign,
  UserCheck,
  Activity,
  Star
} from 'lucide-react';
import { clientService, Client, ClientMetrics } from '@/services/clients';

const ClientManager: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [metrics, setMetrics] = useState<ClientMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: '',
    type: 'enterprise' as Client['type'],
    industry: '',
    size: 'medium' as Client['size'],
    status: 'prospect' as Client['status'],
    contact_person: '',
    email: '',
    phone: '',
    address: '',
    bcm_maturity_level: 1 as Client['bcm_maturity_level'],
    risk_profile: 'medium' as Client['risk_profile'],
    compliance_frameworks: 'ISO 22301',
    modules_subscribed: '',
    contract_status: 'pending_renewal' as Client['contract_status'],
    annual_revenue: 0,
    employee_count: 0
  });

  useEffect(() => {
    loadClients();
    loadMetrics();
  }, []);

  const loadClients = async () => {
    setLoading(true);
    try {
      console.log(' Loading clients from Odoo...');
      const clientsData = await clientService.getAdminClients();
      setClients(clientsData);
      console.log(' Clients loaded:', clientsData.length);
    } catch (error) {
      console.error(' Failed to load clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      const metricsData = await clientService.getClientMetrics();
      setMetrics(metricsData);
    } catch (error) {
      console.error(' Failed to load metrics:', error);
    }
  };

  const handleCreateClient = async () => {
    if (!createForm.name || !createForm.email) return;

    setCreating(true);
    try {
      const clientData = {
        ...createForm,
        compliance_frameworks: createForm.compliance_frameworks.split(',').map(f => f.trim()),
        modules_subscribed: createForm.modules_subscribed.split(',').map(m => m.trim()).filter(Boolean),
        next_review_date: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        last_assessment_date: ''
      };

      console.log(' Creating new client...');
      const success = await clientService.createClient(clientData);

      if (success) {
        console.log(' Client created successfully');
        await loadClients();
        await loadMetrics();
        setCreateDialogOpen(false);
        setCreateForm({
          name: '',
          type: 'enterprise',
          industry: '',
          size: 'medium',
          status: 'prospect',
          contact_person: '',
          email: '',
          phone: '',
          address: '',
          bcm_maturity_level: 1,
          risk_profile: 'medium',
          compliance_frameworks: 'ISO 22301',
          modules_subscribed: '',
          contract_status: 'pending_renewal',
          annual_revenue: 0,
          employee_count: 0
        });
      } else {
        console.error(' Client creation failed');
      }
    } catch (error) {
      console.error(' Create error:', error);
    } finally {
      setCreating(false);
    }
  };

  const filteredClients = clients.filter(client => {
    const matchesStatus = selectedStatus === 'all' || client.status === selectedStatus;
    const matchesType = selectedType === 'all' || client.type === selectedType;
    const matchesSearch = client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         client.industry.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         client.contact_person.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesType && matchesSearch;
  });

  const getStatusColor = (status: Client['status']) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'prospect': return 'bg-blue-100 text-blue-800';
      case 'churned': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskColor = (risk: Client['risk_profile']) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderClientCard = (client: Client) => (
    <Card key={client.id} className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg flex items-center gap-2">
              <Building className="h-5 w-5 text-blue-600" />
              {client.name}
            </CardTitle>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline">{client.type}</Badge>
              <Badge className={getStatusColor(client.status)}>
                {client.status}
              </Badge>
              <Badge className={getRiskColor(client.risk_profile)}>
                {client.risk_profile} risk
              </Badge>
              <div className="flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`h-3 w-3 ${
                      i < client.bcm_maturity_level ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <Button size="sm" variant="ghost">
              <Eye className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="ghost">
              <Edit3 className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="ghost">
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm">
            <UserCheck className="h-4 w-4 text-muted-foreground" />
            <span>{client.contact_person}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Mail className="h-4 w-4 text-muted-foreground" />
            <span>{client.email}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Phone className="h-4 w-4 text-muted-foreground" />
            <span>{client.phone}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span className="truncate">{client.address}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mt-4 pt-3 border-t text-sm">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
            <span>{client.industry}</span>
          </div>
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <span>{client.employee_count} employees</span>
          </div>
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-muted-foreground" />
            <span>{client.compliance_frameworks.length} frameworks</span>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-muted-foreground" />
            <span>{client.modules_subscribed.length} modules</span>
          </div>
        </div>

        {client.next_review_date && (
          <div className="mt-3 pt-3 border-t">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span>Next review: {new Date(client.next_review_date).toLocaleDateString()}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-lg">Loading clients from Odoo...</span>
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
                  <p className="text-sm font-medium text-muted-foreground">Total Clients</p>
                  <p className="text-2xl font-bold">{metrics.total_clients}</p>
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
                  <p className="text-2xl font-bold">{metrics.active_clients}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Plus className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">New This Month</p>
                  <p className="text-2xl font-bold">{metrics.new_clients_this_month}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <AlertTriangle className="h-8 w-8 text-red-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">High Risk</p>
                  <p className="text-2xl font-bold">{metrics.high_risk_clients}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Header with actions */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">BCM Client Management</h3>
          <p className="text-sm text-muted-foreground">
            Manage BCM clients and their subscriptions from Odoo
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Client
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create New Client</DialogTitle>
              </DialogHeader>
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Company Name</Label>
                    <Input
                      value={createForm.name}
                      onChange={(e) => setCreateForm(prev => ({...prev, name: e.target.value}))}
                      placeholder="Company name"
                    />
                  </div>
                  <div>
                    <Label>Contact Person</Label>
                    <Input
                      value={createForm.contact_person}
                      onChange={(e) => setCreateForm(prev => ({...prev, contact_person: e.target.value}))}
                      placeholder="Contact person name"
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
                      placeholder="contact@company.com"
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
                <div>
                  <Label>Address</Label>
                  <Textarea
                    value={createForm.address}
                    onChange={(e) => setCreateForm(prev => ({...prev, address: e.target.value}))}
                    placeholder="Complete address"
                  />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label>Type</Label>
                    <Select
                      value={createForm.type}
                      onValueChange={(value: Client['type']) => setCreateForm(prev => ({...prev, type: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="enterprise">Enterprise</SelectItem>
                        <SelectItem value="government">Government</SelectItem>
                        <SelectItem value="nonprofit">Non-profit</SelectItem>
                        <SelectItem value="startup">Startup</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Size</Label>
                    <Select
                      value={createForm.size}
                      onValueChange={(value: Client['size']) => setCreateForm(prev => ({...prev, size: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="small">Small (1-50)</SelectItem>
                        <SelectItem value="medium">Medium (51-250)</SelectItem>
                        <SelectItem value="large">Large (251-1000)</SelectItem>
                        <SelectItem value="enterprise">Enterprise (1000+)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Industry</Label>
                    <Input
                      value={createForm.industry}
                      onChange={(e) => setCreateForm(prev => ({...prev, industry: e.target.value}))}
                      placeholder="e.g., Technology"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Annual Revenue</Label>
                    <Input
                      type="number"
                      value={createForm.annual_revenue}
                      onChange={(e) => setCreateForm(prev => ({...prev, annual_revenue: parseInt(e.target.value) || 0}))}
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <Label>Employee Count</Label>
                    <Input
                      type="number"
                      value={createForm.employee_count}
                      onChange={(e) => setCreateForm(prev => ({...prev, employee_count: parseInt(e.target.value) || 0}))}
                      placeholder="0"
                    />
                  </div>
                </div>
                <div>
                  <Label>Compliance Frameworks (comma-separated)</Label>
                  <Input
                    value={createForm.compliance_frameworks}
                    onChange={(e) => setCreateForm(prev => ({...prev, compliance_frameworks: e.target.value}))}
                    placeholder="ISO 22301, SOC 2, NIST"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setCreateDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleCreateClient}
                    disabled={creating || !createForm.name || !createForm.email}
                  >
                    {creating ? (
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Plus className="h-4 w-4 mr-2" />
                    )}
                    Create Client
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          <Button variant="outline" onClick={loadClients}>
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
              placeholder="Search clients by name, industry, or contact person..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Select value={selectedStatus} onValueChange={setSelectedStatus}>
          <SelectTrigger className="w-40">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
            <SelectItem value="prospect">Prospect</SelectItem>
            <SelectItem value="churned">Churned</SelectItem>
          </SelectContent>
        </Select>
        <Select value={selectedType} onValueChange={setSelectedType}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="enterprise">Enterprise</SelectItem>
            <SelectItem value="government">Government</SelectItem>
            <SelectItem value="nonprofit">Non-profit</SelectItem>
            <SelectItem value="startup">Startup</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Clients Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredClients.map(renderClientCard)}
      </div>

      {filteredClients.length === 0 && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            No clients found matching your criteria. Try adjusting the search or filters.
          </AlertDescription>
        </Alert>
      )}

      {/* Integration Status */}
      <Alert>
        <CheckCircle className="h-4 w-4" />
        <AlertTitle>Odoo BCM Client Integration</AlertTitle>
        <AlertDescription>
          Client data is synchronized with Odoo partners (res.partner) with BCM subscription flags.
          All client changes are saved directly to the Odoo database with BCM-specific fields.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default ClientManager;