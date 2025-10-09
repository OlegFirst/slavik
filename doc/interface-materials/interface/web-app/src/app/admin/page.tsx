'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { MainLayout } from '@/components/layout/main-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { Activity, Server, Database, Zap, AlertCircle, CheckCircle2 } from 'lucide-react'

export default function AdminPage() {
  const { data: services, isLoading } = useQuery({
    queryKey: ['admin', 'health'],
    queryFn: () => apiClient.getServiceHealth(),
    refetchInterval: 30000, // Refresh every 30 seconds
    // Mock data for development
    placeholderData: [
      {
        service_name: 'BIA Service',
        status: 'healthy',
        uptime: 99.9,
        last_check: new Date().toISOString(),
        response_time_ms: 45,
        error_count: 0,
      },
      {
        service_name: 'Risk Service',
        status: 'healthy',
        uptime: 99.8,
        last_check: new Date().toISOString(),
        response_time_ms: 52,
        error_count: 0,
      },
      {
        service_name: 'Compliance Service',
        status: 'healthy',
        uptime: 99.7,
        last_check: new Date().toISOString(),
        response_time_ms: 38,
        error_count: 0,
      },
      {
        service_name: 'Governance Service',
        status: 'degraded',
        uptime: 98.5,
        last_check: new Date().toISOString(),
        response_time_ms: 150,
        error_count: 3,
      },
      {
        service_name: 'Documents Service',
        status: 'healthy',
        uptime: 99.9,
        last_check: new Date().toISOString(),
        response_time_ms: 41,
        error_count: 0,
      },
      {
        service_name: 'Workflow Intelligence',
        status: 'healthy',
        uptime: 99.6,
        last_check: new Date().toISOString(),
        response_time_ms: 68,
        error_count: 0,
      },
      {
        service_name: 'AI Foundation',
        status: 'healthy',
        uptime: 99.5,
        last_check: new Date().toISOString(),
        response_time_ms: 120,
        error_count: 0,
      },
      {
        service_name: 'PostgreSQL Database',
        status: 'healthy',
        uptime: 99.99,
        last_check: new Date().toISOString(),
        response_time_ms: 12,
        error_count: 0,
      },
      {
        service_name: 'RabbitMQ EventBus',
        status: 'healthy',
        uptime: 99.9,
        last_check: new Date().toISOString(),
        response_time_ms: 8,
        error_count: 0,
      },
    ],
  })

  const healthyCount = services?.filter((s) => s.status === 'healthy').length || 0
  const degradedCount = services?.filter((s) => s.status === 'degraded').length || 0
  const downCount = services?.filter((s) => s.status === 'down').length || 0

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Administration</h1>
          <p className="text-muted-foreground">
            Monitor and manage platform services and infrastructure
          </p>
        </div>

        {/* Overall Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Services</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{services?.length || 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Healthy</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-500">{healthyCount}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Degraded</CardTitle>
              <AlertCircle className="h-4 w-4 text-yellow-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-500">{degradedCount}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Down</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-500">{downCount}</div>
            </CardContent>
          </Card>
        </div>

        {/* Service Categories */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Platform Services */}
          <Card>
            <CardHeader>
              <CardTitle>Platform Services</CardTitle>
              <CardDescription>Business logic and domain services</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {services
                ?.filter((s) =>
                  [
                    'BIA Service',
                    'Risk Service',
                    'Compliance Service',
                    'Governance Service',
                    'Documents Service',
                  ].includes(s.service_name)
                )
                .map((service) => (
                  <ServiceCard key={service.service_name} service={service} />
                ))}
            </CardContent>
          </Card>

          {/* Intelligent Core */}
          <Card>
            <CardHeader>
              <CardTitle>Intelligent Core</CardTitle>
              <CardDescription>AI and workflow intelligence services</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {services
                ?.filter((s) =>
                  ['Workflow Intelligence', 'AI Foundation'].includes(s.service_name)
                )
                .map((service) => (
                  <ServiceCard key={service.service_name} service={service} />
                ))}
            </CardContent>
          </Card>

          {/* Infrastructure */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Infrastructure</CardTitle>
              <CardDescription>Core infrastructure components</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              {services
                ?.filter((s) =>
                  ['PostgreSQL Database', 'RabbitMQ EventBus'].includes(s.service_name)
                )
                .map((service) => (
                  <ServiceCard key={service.service_name} service={service} />
                ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  )
}

function ServiceCard({ service }: { service: any }) {
  const statusConfig = {
    healthy: {
      color: 'success',
      icon: CheckCircle2,
      textColor: 'text-green-500',
    },
    degraded: {
      color: 'warning',
      icon: AlertCircle,
      textColor: 'text-yellow-500',
    },
    down: {
      color: 'destructive',
      icon: AlertCircle,
      textColor: 'text-red-500',
    },
  }

  const config = statusConfig[service.status as keyof typeof statusConfig]
  const Icon = config.icon

  return (
    <div className="flex items-start gap-4 p-4 border rounded-lg">
      <div className={`mt-1 ${config.textColor}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="flex-1 space-y-2">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold">{service.service_name}</h4>
          <Badge variant={config.color as any}>{service.status}</Badge>
        </div>
        <div className="space-y-1 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Uptime</span>
            <span className="font-medium">{service.uptime}%</span>
          </div>
          <Progress value={service.uptime} className="h-1" />
          <div className="flex justify-between">
            <span className="text-muted-foreground">Response Time</span>
            <span className="font-medium">{service.response_time_ms}ms</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Errors</span>
            <span className={service.error_count > 0 ? 'text-red-500 font-medium' : ''}>
              {service.error_count}
            </span>
          </div>
        </div>
        <p className="text-xs text-muted-foreground">
          Last checked: {new Date(service.last_check).toLocaleTimeString()}
        </p>
      </div>
    </div>
  )
}
