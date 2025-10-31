import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Package,
  Search,
  RefreshCw,
  Download,
  Upload,
  Archive,
  Trash2,
  Eye,
  Settings,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Database,
  FileText,
  HardDrive,
  Zap,
  Activity,
  TrendingUp,
  TrendingDown,
  Minus,
  Shield,
  Lock,
  Unlock,
  Copy,
  ExternalLink
} from 'lucide-react';
import { digitalTwinAPI, TwinDataPackage, PackageStats, TransportLog } from '@/services/digitalTwinAPI';
import { useDataPackages, useRealTimeMetrics } from '@/contexts/DigitalTwinContext';

interface PackageManagerProps {
  className?: string;
}

interface PackageFilter {
  status: string;
  type: string;
  dateRange: string;
}

const PackageManager: React.FC<PackageManagerProps> = ({ className }) => {
  const { packages, connected } = useDataPackages();
  const [filteredPackages, setFilteredPackages] = useState<TwinDataPackage[]>([]);
  const [packageStats, setPackageStats] = useState<PackageStats | null>(null);
  const [transportLogs, setTransportLogs] = useState<TransportLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [livePackageUpdates, setLivePackageUpdates] = useState<Map<string, any>>(new Map());
  const [activeOperations, setActiveOperations] = useState<Map<string, any>>(new Map());
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<PackageFilter>({
    status: 'all',
    type: 'all',
    dateRange: 'all'
  });
  const [selectedPackage, setSelectedPackage] = useState<TwinDataPackage | null>(null);
  const [packageDetails, setPackageDetails] = useState<any>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [isUploading, setIsUploading] = useState(false);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(15);

  // Real-time package updates
  useRealTimeMetrics('package_update', (data) => {
    setLivePackageUpdates(prev => {
      const updated = new Map(prev);
      updated.set(data.packageId, {
        ...data,
        timestamp: new Date()
      });
      return updated;
    });
  });

  // Real-time package operations (upload, download, verify, etc.)
  useRealTimeMetrics('package_operation', (data) => {
    setActiveOperations(prev => {
      const updated = new Map(prev);
      if (data.status === 'completed' || data.status === 'failed') {
        updated.delete(data.operationId);
      } else {
        updated.set(data.operationId, {
          ...data,
          timestamp: new Date()
        });
      }
      return updated;
    });
  });

  // Real-time transport logs
  useRealTimeMetrics('transport_log', (data) => {
    setTransportLogs(prev => [data, ...prev.slice(0, 49)]); // Keep last 50 logs
  });

  useEffect(() => {
    loadPackages();
    loadTransportLogs();
  }, []);

  useEffect(() => {
    filterPackages();
  }, [packages, searchTerm, filters]);

  const loadPackages = async () => {
    try {
      setLoading(true);
      // If connected to real-time, packages are automatically updated
      if (!connected) {
        const [packagesData, statsData] = await Promise.all([
          digitalTwinAPI.getTwinDataPackages(),
          digitalTwinAPI.getPackageStats()
        ]);
        setPackageStats(statsData);
      } else {
        // Just load stats as packages come through real-time
        const statsData = await digitalTwinAPI.getPackageStats();
        setPackageStats(statsData);
      }
      setError(null);
    } catch (err) {
      console.error('Failed to load packages:', err);
      setError('Failed to load data packages');
    } finally {
      setLoading(false);
    }
  };

  const loadTransportLogs = async () => {
    try {
      const logs = await digitalTwinAPI.getTransportLogs();
      setTransportLogs(logs);
    } catch (err) {
      console.error('Failed to load transport logs:', err);
    }
  };

  const filterPackages = () => {
    let filtered = packages;

    if (searchTerm) {
      filtered = filtered.filter(pkg =>
        pkg.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        pkg.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        pkg.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        pkg.owner.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filters.status !== 'all') {
      filtered = filtered.filter(pkg => pkg.status === filters.status);
    }

    if (filters.type !== 'all') {
      filtered = filtered.filter(pkg => pkg.type === filters.type);
    }

    if (filters.dateRange !== 'all') {
      const now = new Date();
      const cutoff = new Date();

      switch (filters.dateRange) {
        case 'today':
          cutoff.setDate(now.getDate() - 1);
          break;
        case 'week':
          cutoff.setDate(now.getDate() - 7);
          break;
        case 'month':
          cutoff.setMonth(now.getMonth() - 1);
          break;
      }

      filtered = filtered.filter(pkg => new Date(pkg.createdAt) >= cutoff);
    }

    setFilteredPackages(filtered);
    setCurrentPage(1);
  };

  const handlePackageAction = async (packageId: string, action: string) => {
    try {
      setLoading(true);
      switch (action) {
        case 'download':
          await digitalTwinAPI.downloadPackage(packageId);
          break;
        case 'verify':
          await digitalTwinAPI.verifyPackage(packageId);
          break;
        case 'archive':
          await digitalTwinAPI.archivePackage(packageId);
          break;
        case 'delete':
          if (window.confirm('Are you sure you want to delete this package?')) {
            await digitalTwinAPI.deletePackage(packageId);
          }
          break;
        case 'clone':
          await digitalTwinAPI.clonePackage(packageId);
          break;
      }
      await loadPackages();
    } catch (err) {
      console.error(`Failed to ${action} package:`, err);
      setError(`Failed to ${action} package`);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (pkg: TwinDataPackage) => {
    try {
      setSelectedPackage(pkg);
      setLoading(true);
      const details = await digitalTwinAPI.getPackageDetails(pkg.id);
      setPackageDetails(details);
      setIsDetailsOpen(true);
    } catch (err) {
      console.error('Failed to load package details:', err);
      setError('Failed to load package details');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    const operationId = `upload-${Date.now()}`;
    try {
      setIsUploading(true);
      setUploadProgress(0);

      // Add to active operations
      setActiveOperations(prev => {
        const updated = new Map(prev);
        updated.set(operationId, {
          type: 'upload',
          fileName: file.name,
          status: 'uploading',
          progress: 0,
          timestamp: new Date()
        });
        return updated;
      });

      // Real-time progress updates will come through WebSocket
      // Simulate upload progress if not connected
      let progressInterval: NodeJS.Timeout | null = null;
      if (!connected) {
        progressInterval = setInterval(() => {
          setUploadProgress(prev => {
            if (prev >= 95) {
              if (progressInterval) clearInterval(progressInterval);
              return 95;
            }
            return prev + 5;
          });
        }, 100);
      }

      await digitalTwinAPI.uploadPackage(file);

      if (progressInterval) clearInterval(progressInterval);
      setUploadProgress(100);

      // Remove from active operations
      setActiveOperations(prev => {
        const updated = new Map(prev);
        updated.delete(operationId);
        return updated;
      });

      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress(0);
        if (!connected) loadPackages();
      }, 1000);
    } catch (err) {
      console.error('Failed to upload package:', err);
      setError('Failed to upload package');
      setIsUploading(false);
      setUploadProgress(0);

      // Update operation status
      setActiveOperations(prev => {
        const updated = new Map(prev);
        updated.set(operationId, {
          type: 'upload',
          fileName: file.name,
          status: 'failed',
          timestamp: new Date()
        });
        return updated;
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <Activity className="h-4 w-4 text-blue-500 animate-pulse" />;
      case 'archived':
        return <Archive className="h-4 w-4 text-gray-500" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'uploading':
        return <Upload className="h-4 w-4 text-blue-500 animate-bounce" />;
      default:
        return <Package className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'text-green-600 bg-green-100';
      case 'processing':
        return 'text-blue-600 bg-blue-100';
      case 'archived':
        return 'text-gray-600 bg-gray-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'uploading':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getCompressionColor = (ratio: number) => {
    if (ratio >= 70) return 'text-green-600';
    if (ratio >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Pagination logic
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentPackages = filteredPackages.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredPackages.length / itemsPerPage);

  if (loading && packages.length === 0) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="space-y-3">
            {[...Array(8)].map((_, i) => (
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
          <h2 className="text-2xl font-bold">Package Management</h2>
          <p className="text-gray-600">Manage TwinDataPackages and transport</p>
        </div>
        <div className="flex space-x-2">
          <input
            type="file"
            id="package-upload"
            className="hidden"
            accept=".pkg,.zip,.tar.gz"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFileUpload(file);
            }}
          />
          <Button
            variant="outline"
            onClick={() => document.getElementById('package-upload')?.click()}
            disabled={isUploading}
          >
            <Upload className="h-4 w-4 mr-2" />
            Upload Package
          </Button>

          {/* Real-time Status */}
          <Badge className={connected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'} variant="secondary">
            {connected ? (
              <><Activity className="h-3 w-3 mr-1 animate-pulse" />Live ({packages.length} packages)</>
            ) : (
              <><WifiOff className="h-3 w-3 mr-1" />Offline</>
            )}
          </Badge>

          {/* Active Operations Counter */}
          {activeOperations.size > 0 && (
            <Badge variant="outline" className="text-blue-600">
              <Zap className="h-3 w-3 mr-1 animate-pulse" />
              {activeOperations.size} active ops
            </Badge>
          )}

          <Button variant="outline" onClick={loadPackages} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Export All
          </Button>
        </div>
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <Alert>
          <Upload className="h-4 w-4" />
          <AlertDescription>
            <div className="flex items-center space-x-2">
              <span>Uploading package...</span>
              <Progress value={uploadProgress} className="flex-1" />
              <span>{uploadProgress}%</span>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Error Alert */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Package className="h-8 w-8 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">{packages.length}</div>
                <div className="text-sm text-gray-600">Total Packages</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <HardDrive className="h-8 w-8 text-purple-500" />
              <div>
                <div className="text-2xl font-bold">
                  {packageStats?.totalSize ? formatFileSize(packageStats.totalSize) : '0 MB'}
                </div>
                <div className="text-sm text-gray-600">Total Size</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Zap className="h-8 w-8 text-green-500" />
              <div>
                <div className="text-2xl font-bold">
                  {packageStats?.avgCompressionRatio || 0}%
                </div>
                <div className="text-sm text-gray-600">Avg Compression</div>
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
                  {packages.filter(p => p.status === 'ready').length}
                </div>
                <div className="text-sm text-gray-600">Ready</div>
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
                  placeholder="Search packages by name, description, ID, or owner..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex space-x-2">
              <select
                value={filters.status}
                onChange={(e) => setFilters({...filters, status: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="all">All Status</option>
                <option value="ready">Ready</option>
                <option value="processing">Processing</option>
                <option value="archived">Archived</option>
                <option value="error">Error</option>
              </select>

              <select
                value={filters.type}
                onChange={(e) => setFilters({...filters, type: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="all">All Types</option>
                <option value="personal">Personal</option>
                <option value="organizational">Organizational</option>
                <option value="backup">Backup</option>
                <option value="export">Export</option>
              </select>

              <select
                value={filters.dateRange}
                onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs defaultValue="packages" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="packages">Packages</TabsTrigger>
          <TabsTrigger value="transport">Transport Logs</TabsTrigger>
        </TabsList>

        <TabsContent value="packages" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Data Packages ({filteredPackages.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {currentPackages.map((pkg) => (
                  <div key={pkg.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-center space-x-4 flex-1">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(pkg.status)}
                        <Badge className={getStatusColor(pkg.status)} variant="secondary">
                          {pkg.status}
                        </Badge>
                      </div>

                      <div className="flex-1">
                        <div className="font-medium">{pkg.name}</div>
                        <div className="text-sm text-gray-600">{pkg.description}</div>
                        <div className="text-xs text-gray-500">
                          ID: {pkg.id} | Owner: {pkg.owner}
                        </div>
                      </div>

                      <div className="text-center">
                        <div className="text-sm font-medium">{formatFileSize(pkg.size)}</div>
                        <div className="text-xs text-gray-500">Size</div>
                      </div>

                      <div className="text-center">
                        <div className={`text-sm font-medium ${getCompressionColor(pkg.compressionRatio)}`}>
                          {pkg.compressionRatio}%
                        </div>
                        <div className="text-xs text-gray-500">Compression</div>
                      </div>

                      <div className="text-center">
                        <div className="text-sm font-medium">{pkg.type}</div>
                        <div className="text-xs text-gray-500">Type</div>
                      </div>

                      <div className="text-center">
                        <div className="text-sm font-medium">{pkg.createdAt}</div>
                        <div className="text-xs text-gray-500">Created</div>
                      </div>

                      <div className="text-center">
                        {pkg.encrypted ? (
                          <Lock className="h-4 w-4 text-green-500 mx-auto" />
                        ) : (
                          <Unlock className="h-4 w-4 text-gray-400 mx-auto" />
                        )}
                        <div className="text-xs text-gray-500">
                          {pkg.encrypted ? 'Encrypted' : 'Plain'}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleViewDetails(pkg)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePackageAction(pkg.id, 'download')}
                      >
                        <Download className="h-4 w-4" />
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePackageAction(pkg.id, 'verify')}
                      >
                        <Shield className="h-4 w-4" />
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePackageAction(pkg.id, 'clone')}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePackageAction(pkg.id, 'archive')}
                        disabled={pkg.status === 'archived'}
                      >
                        <Archive className="h-4 w-4" />
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePackageAction(pkg.id, 'delete')}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}

                {currentPackages.length === 0 && (
                  <div className="text-center py-8">
                    <Package className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">No packages found</p>
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
        </TabsContent>

        <TabsContent value="transport" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Transport Logs</CardTitle>
              <CardDescription>Package transfer and transport activity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {transportLogs.map((log) => (
                  <div key={log.id} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                    {getStatusIcon(log.status)}
                    <div className="flex-1">
                      <div className="font-medium">{log.action}</div>
                      <div className="text-sm text-gray-600">
                        Package: {log.packageName} | Size: {formatFileSize(log.size)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">{log.timestamp}</div>
                      <div className="text-xs text-gray-500">{log.duration}</div>
                    </div>
                  </div>
                ))}

                {transportLogs.length === 0 && (
                  <div className="text-center py-8">
                    <Activity className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">No transport activity</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Package Details Modal */}
      <Dialog open={isDetailsOpen} onOpenChange={setIsDetailsOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Package className="h-5 w-5" />
              <span>Package Details - {selectedPackage?.name}</span>
            </DialogTitle>
            <DialogDescription>
              Comprehensive package information and metadata
            </DialogDescription>
          </DialogHeader>

          {packageDetails && (
            <div className="space-y-6">
              {/* Package Info */}
              <div>
                <h4 className="font-medium mb-3">Package Information</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">ID:</span>
                    <span className="ml-2">{packageDetails.id}</span>
                  </div>
                  <div>
                    <span className="font-medium">Type:</span>
                    <span className="ml-2">{packageDetails.type}</span>
                  </div>
                  <div>
                    <span className="font-medium">Owner:</span>
                    <span className="ml-2">{packageDetails.owner}</span>
                  </div>
                  <div>
                    <span className="font-medium">Created:</span>
                    <span className="ml-2">{packageDetails.createdAt}</span>
                  </div>
                  <div>
                    <span className="font-medium">Size:</span>
                    <span className="ml-2">{formatFileSize(packageDetails.size)}</span>
                  </div>
                  <div>
                    <span className="font-medium">Compression:</span>
                    <span className="ml-2">{packageDetails.compressionRatio}%</span>
                  </div>
                </div>
              </div>

              {/* Contents */}
              <div>
                <h4 className="font-medium mb-3">Package Contents</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {packageDetails.contents?.map((item: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex items-center space-x-2">
                        <FileText className="h-4 w-4 text-gray-500" />
                        <span className="text-sm">{item.name}</span>
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatFileSize(item.size)}
                      </div>
                    </div>
                  )) || (
                    <div className="text-center text-gray-500 py-4">
                      No content information available
                    </div>
                  )}
                </div>
              </div>

              {/* Metadata */}
              {packageDetails.metadata && (
                <div>
                  <h4 className="font-medium mb-3">Metadata</h4>
                  <div className="bg-gray-50 p-3 rounded text-sm font-mono">
                    <pre>{JSON.stringify(packageDetails.metadata, null, 2)}</pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PackageManager;