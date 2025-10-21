/**
 * Service Catalog Page
 * ====================
 * Displays all 47 platform services with health status, categories, and metrics
 */

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  useServiceCatalog,
  useServiceCatalogStats,
  useServicesByCategory,
  useMissingServices,
  useUnknownServices,
} from '@/hooks/useServiceCatalog';
import { ServiceCatalogService } from '@/services/service-catalog-api';
import {
  Search,
  Activity,
  Server,
  AlertCircle,
  CheckCircle,
  XCircle,
  HelpCircle,
  TrendingUp,
  Package,
} from 'lucide-react';

export const ServiceCatalog: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const { data: services, isLoading: servicesLoading } = useServiceCatalog(30000);
  const { data: stats, isLoading: statsLoading } = useServiceCatalogStats(30000);
  const { data: categories, isLoading: categoriesLoading } = useServicesByCategory(30000);
  const { data: missingServices } = useMissingServices(30000);
  const { data: unknownServices } = useUnknownServices(30000);

  // Filter services based on search and category
  const filteredServices = services?.filter(service => {
    const matchesSearch = searchQuery === '' ||
      service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      service.display_name?.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesCategory = selectedCategory === null ||
      service.type === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Service Catalog</h1>
            <p className="text-muted-foreground mt-1">
              Platform-wide service registry with {stats?.totals.total_services || 47} services
            </p>
          </div>
          <Badge variant="outline" className="text-lg px-4 py-2">
            v{stats?.metadata.version || '3.0.0'}
          </Badge>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Services</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.totals.total_services || 0}</div>
              <p className="text-xs text-muted-foreground">
                {stats?.totals.registered_services || 0} registered
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Healthy Services</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {stats?.totals.healthy_services || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Running and operational
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Missing Services</CardTitle>
              <AlertCircle className="h-4 w-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {stats?.totals.missing_services || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                In catalog but not running
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Coverage</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats?.totals.coverage_percent.toFixed(1) || 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                Services operational
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search services..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button
                variant={selectedCategory === null ? 'default' : 'outline'}
                onClick={() => setSelectedCategory(null)}
              >
                All Services
              </Button>
            </div>

            {/* Category Pills */}
            <div className="flex flex-wrap gap-2 mt-4">
              {categories?.map(category => (
                <Badge
                  key={category.name}
                  variant={selectedCategory === category.name ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => setSelectedCategory(
                    selectedCategory === category.name ? null : category.name
                  )}
                >
                  {category.name} ({category.count})
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Services Tabs */}
        <Tabs defaultValue="all" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all">
              All Services ({filteredServices?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="healthy">
              Healthy ({stats?.totals.healthy_services || 0})
            </TabsTrigger>
            <TabsTrigger value="missing">
              Missing ({stats?.totals.missing_services || 0})
            </TabsTrigger>
            <TabsTrigger value="unknown">
              Unknown ({stats?.totals.unknown_services || 0})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-4">
            <ServiceList services={filteredServices || []} />
          </TabsContent>

          <TabsContent value="healthy" className="mt-4">
            <ServiceList
              services={filteredServices?.filter(s => s.health_status === 'healthy') || []}
            />
          </TabsContent>

          <TabsContent value="missing" className="mt-4">
            <ServiceList services={missingServices || []} />
          </TabsContent>

          <TabsContent value="unknown" className="mt-4">
            <ServiceList services={unknownServices || []} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// Service List Component
const ServiceList: React.FC<{ services: ServiceCatalogService[] }> = ({ services }) => {
  if (services.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          No services found
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {services.map(service => (
        <ServiceCard key={service.name} service={service} />
      ))}
    </div>
  );
};

// Service Card Component
const ServiceCard: React.FC<{ service: ServiceCatalogService }> = ({ service }) => {
  const healthIcon = {
    healthy: <CheckCircle className="h-5 w-5 text-green-500" />,
    degraded: <AlertCircle className="h-5 w-5 text-orange-500" />,
    unhealthy: <XCircle className="h-5 w-5 text-red-500" />,
    unknown: <HelpCircle className="h-5 w-5 text-gray-500" />,
  }[service.health_status];

  const registrationColor = {
    registered: 'default',
    missing: 'destructive',
    unknown: 'secondary',
  }[service.registration_status] as 'default' | 'destructive' | 'secondary';

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              {healthIcon}
              <CardTitle className="text-lg">
                {service.display_name || service.name}
              </CardTitle>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              {service.name}
            </p>
          </div>
          <Badge variant={registrationColor}>
            {service.registration_status}
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-3">
          {/* Port */}
          {(service.expected_port || service.actual_port) && (
            <div className="flex items-center gap-2 text-sm">
              <Server className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Port:</span>
              <span className="font-mono">
                {service.actual_port || service.expected_port}
              </span>
            </div>
          )}

          {/* Type/Category */}
          <div className="flex items-center gap-2 text-sm">
            <Activity className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Type:</span>
            <Badge variant="outline" className="text-xs">
              {service.type}
            </Badge>
          </div>

          {/* Version */}
          {service.version && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">Version:</span>
              <span className="font-mono text-xs">{service.version}</span>
            </div>
          )}

          {/* Description */}
          {service.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mt-2">
              {service.description}
            </p>
          )}

          {/* Business Process Tags */}
          {service.business_process && service.business_process.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {service.business_process.slice(0, 2).map((bp, idx) => (
                <Badge key={idx} variant="secondary" className="text-xs">
                  {bp}
                </Badge>
              ))}
              {service.business_process.length > 2 && (
                <Badge variant="secondary" className="text-xs">
                  +{service.business_process.length - 2}
                </Badge>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ServiceCatalog;
