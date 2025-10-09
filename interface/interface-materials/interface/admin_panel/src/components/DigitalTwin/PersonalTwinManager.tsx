import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  User,
  Search,
  Filter,
  Settings,
  Eye,
  RefreshCw,
  Trash2,
  Download,
  Upload,
  Shield,
  Activity,
  Clock,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Database,
  Brain,
  Zap,
  Users,
  Calendar,
  TrendingUp,
  XCircle
} from 'lucide-react';
import { digitalTwinAPI, PersonalTwin, TwinHealthScore, TwinActivity } from '@/services/digitalTwinAPI';
import { usePersonalTwins, useRealTimeMetrics } from '@/contexts/DigitalTwinContext';

interface PersonalTwinManagerProps {
  className?: string;
}

const PersonalTwinManager: React.FC<PersonalTwinManagerProps> = ({ className }) => {
  const { personalTwins: twins, connected } = usePersonalTwins();
  const [filteredTwins, setFilteredTwins] = useState<PersonalTwin[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [liveTwinUpdates, setLiveTwinUpdates] = useState<Map<string, any>>(new Map());
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedTwin, setSelectedTwin] = useState<PersonalTwin | null>(null);
  const [twinDetails, setTwinDetails] = useState<any>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  // Real-time twin updates subscription
  useRealTimeMetrics('personal_twin_update', (data) => {
    setLiveTwinUpdates(prev => {
      const updated = new Map(prev);
      updated.set(data.twinId, {
        ...data,
        timestamp: new Date()
      });
      return updated;
    });
  });

  // Real-time sync status updates
  useRealTimeMetrics('twin_sync_status', (data) => {
    console.log('Twin sync status update:', data);
  });

  useEffect(() => {
    filterTwins();
  }, [twins, searchTerm, statusFilter]);

  const loadTwins = async () => {
    try {
      setLoading(true);
      // If connected to real-time, twins are automatically updated
      if (!connected) {
        const data = await digitalTwinAPI.getPersonalTwins();
        // This would update the context, but since we're not connected,
        // we'll handle it in the catch block
      }
      setError(null);
    } catch (err) {
      console.error('Failed to load personal twins:', err);
      setError('Failed to load personal twins');
    } finally {
      setLoading(false);
    }
  };

  const filterTwins = () => {
    let filtered = twins;

    if (searchTerm) {
      filtered = filtered.filter(twin =>
        twin.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        twin.userEmail.toLowerCase().includes(searchTerm.toLowerCase()) ||
        twin.id.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(twin => twin.status === statusFilter);
    }

    setFilteredTwins(filtered);
    setCurrentPage(1);
  };

  const handleTwinAction = async (twinId: string, action: string) => {
    try {
      setLoading(true);
      switch (action) {
        case 'sync':
          await digitalTwinAPI.syncPersonalTwin(twinId);
          break;
        case 'reset':
          await digitalTwinAPI.resetPersonalTwin(twinId);
          break;
        case 'analyze':
          await digitalTwinAPI.analyzePersonalTwin(twinId);
          break;
        case 'delete':
          if (window.confirm('Are you sure you want to delete this Digital Twin?')) {
            await digitalTwinAPI.deletePersonalTwin(twinId);
          }
          break;
      }
      await loadTwins();
    } catch (err) {
      console.error(`Failed to ${action} twin:`, err);
      setError(`Failed to ${action} twin`);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (twin: PersonalTwin) => {
    try {
      setSelectedTwin(twin);
      setLoading(true);
      const details = await digitalTwinAPI.getPersonalTwinDetails(twin.id);
      setTwinDetails(details);
      setIsDetailsOpen(true);
    } catch (err) {
      console.error('Failed to load twin details:', err);
      setError('Failed to load twin details');
    } finally {
      setLoading(false);
    }
  };

  const handlePrivacyToggle = async (twinId: string, setting: string, value: boolean) => {
    try {
      await digitalTwinAPI.updatePrivacySettings(twinId, { [setting]: value });
      await loadTwins();
    } catch (err) {
      console.error('Failed to update privacy settings:', err);
      setError('Failed to update privacy settings');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'inactive':
        return <XCircle className="h-4 w-4 text-gray-500" />;
      case 'syncing':
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'inactive':
        return 'text-gray-600 bg-gray-100';
      case 'syncing':
        return 'text-blue-600 bg-blue-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Pagination logic
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentTwins = filteredTwins.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredTwins.length / itemsPerPage);

  if (loading && twins.length === 0) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Personal Twin Management</h2>
          <p className="text-gray-600">Manage individual user Digital Twins</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={loadTwins} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-8 w-8 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">{twins.length}</div>
                <div className="text-sm text-gray-600">Total Twins</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-8 w-8 text-green-500" />
              <div>
                <div className="text-2xl font-bold">
                  {twins.filter(t => t.status === 'active').length}
                </div>
                <div className="text-sm text-gray-600">Active</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <RefreshCw className="h-8 w-8 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">
                  {twins.filter(t => t.status === 'syncing').length}
                </div>
                <div className="text-sm text-gray-600">Syncing</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-8 w-8 text-purple-500" />
              <div>
                <div className="text-2xl font-bold">
                  {twins.length > 0
                    ? Math.round(twins.reduce((sum, t) => sum + t.healthScore, 0) / twins.length)
                    : 0}%
                </div>
                <div className="text-sm text-gray-600">Avg Health</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search by name, email, or ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex space-x-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="syncing">Syncing</option>
                <option value="error">Error</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Twins List */}
      <Card>
        <CardHeader>
          <CardTitle>Personal Digital Twins ({filteredTwins.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {currentTwins.map((twin) => (
              <div key={twin.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex items-center space-x-4 flex-1">
                  <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                    <User className="h-6 w-6 text-gray-600" />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium">{twin.userName}</h4>
                      {getStatusIcon(twin.status)}
                      <Badge className={getStatusColor(twin.status)} variant="secondary">
                        {twin.status}
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-600">{twin.userEmail}</div>
                    <div className="text-xs text-gray-500">ID: {twin.id}</div>
                  </div>

                  <div className="text-center">
                    <div className={`text-lg font-bold ${getHealthColor(twin.healthScore)}`}>
                      {twin.healthScore}%
                    </div>
                    <div className="text-xs text-gray-500">Health Score</div>
                  </div>

                  <div className="text-center">
                    <div className="text-sm font-medium">{twin.lastSync}</div>
                    <div className="text-xs text-gray-500">Last Sync</div>
                  </div>

                  <div className="text-center">
                    <div className="text-sm font-medium">{twin.dataPoints.toLocaleString()}</div>
                    <div className="text-xs text-gray-500">Data Points</div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleViewDetails(twin)}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleTwinAction(twin.id, 'sync')}
                    disabled={twin.status === 'syncing'}
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleTwinAction(twin.id, 'analyze')}
                  >
                    <BarChart3 className="h-4 w-4" />
                  </Button>

                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="outline" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Privacy Settings - {twin.userName}</DialogTitle>
                        <DialogDescription>
                          Manage data collection and privacy preferences
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <Label htmlFor="behavior-tracking">Behavior Tracking</Label>
                          <Switch
                            id="behavior-tracking"
                            checked={twin.privacySettings?.behaviorTracking || false}
                            onCheckedChange={(checked) =>
                              handlePrivacyToggle(twin.id, 'behaviorTracking', checked)
                            }
                          />
                        </div>
                        <div className="flex items-center justify-between">
                          <Label htmlFor="performance-monitoring">Performance Monitoring</Label>
                          <Switch
                            id="performance-monitoring"
                            checked={twin.privacySettings?.performanceMonitoring || false}
                            onCheckedChange={(checked) =>
                              handlePrivacyToggle(twin.id, 'performanceMonitoring', checked)
                            }
                          />
                        </div>
                        <div className="flex items-center justify-between">
                          <Label htmlFor="ai-insights">AI Insights</Label>
                          <Switch
                            id="ai-insights"
                            checked={twin.privacySettings?.aiInsights || false}
                            onCheckedChange={(checked) =>
                              handlePrivacyToggle(twin.id, 'aiInsights', checked)
                            }
                          />
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleTwinAction(twin.id, 'delete')}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}

            {currentTwins.length === 0 && (
              <div className="text-center py-8">
                <User className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600">No personal twins found</p>
              </div>
            )}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-2 mt-6">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
              >
                Previous
              </Button>

              <span className="text-sm text-gray-600">
                Page {currentPage} of {totalPages}
              </span>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Twin Details Modal */}
      <Dialog open={isDetailsOpen} onOpenChange={setIsDetailsOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <User className="h-5 w-5" />
              <span>Digital Twin Details - {selectedTwin?.userName}</span>
            </DialogTitle>
            <DialogDescription>
              Comprehensive view of Digital Twin data and activity
            </DialogDescription>
          </DialogHeader>

          {twinDetails && (
            <div className="space-y-6">
              {/* Health Metrics */}
              <div>
                <h4 className="font-medium mb-3">Health Metrics</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-green-600">
                      {twinDetails.health?.dataQuality || 0}%
                    </div>
                    <div className="text-xs text-gray-600">Data Quality</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-blue-600">
                      {twinDetails.health?.completeness || 0}%
                    </div>
                    <div className="text-xs text-gray-600">Completeness</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-purple-600">
                      {twinDetails.health?.accuracy || 0}%
                    </div>
                    <div className="text-xs text-gray-600">Accuracy</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-orange-600">
                      {twinDetails.health?.freshness || 0}%
                    </div>
                    <div className="text-xs text-gray-600">Freshness</div>
                  </div>
                </div>
              </div>

              {/* Activity Timeline */}
              <div>
                <h4 className="font-medium mb-3">Recent Activity</h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {twinDetails.activities?.map((activity: any, index: number) => (
                    <div key={index} className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                      <Activity className="h-4 w-4 text-gray-500" />
                      <div className="flex-1">
                        <div className="text-sm font-medium">{activity.action}</div>
                        <div className="text-xs text-gray-600">{activity.timestamp}</div>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {activity.type}
                      </Badge>
                    </div>
                  )) || (
                    <div className="text-center text-gray-500 py-4">
                      No recent activity
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PersonalTwinManager;