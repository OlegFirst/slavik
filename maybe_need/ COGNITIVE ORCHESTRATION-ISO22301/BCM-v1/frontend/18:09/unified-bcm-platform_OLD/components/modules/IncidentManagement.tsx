'use client'

import { useState, useEffect } from 'react'
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
import {
  AlertTriangle,
  Clock,
  Users,
  CheckCircle,
  XCircle,
  AlertCircle,
  Activity,
  PhoneCall,
  MessageSquare,
  FileText,
  Timer,
  Target,
  Shield,
  Zap,
  TrendingUp,
  ChevronRight,
  Search,
  Filter,
  Download,
  Upload,
  RefreshCw,
  Settings,
  Bell,
  UserCheck,
  MapPin,
  Siren
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useBCMStore } from '@/lib/bcm-store'

// Types
interface Incident {
  id: string
  title: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  status: 'detected' | 'assessing' | 'responding' | 'recovering' | 'resolved' | 'closed'
  type: 'operational' | 'cyber' | 'natural_disaster' | 'health_safety' | 'supply_chain' | 'other'
  detectedAt: string
  reportedBy: string
  assignedTo: string[]
  impactedAreas: string[]
  estimatedRTO: number // in minutes
  actualRTO?: number
  estimatedRecoveryCost: number
  timeline: TimelineEvent[]
  responseTeam: TeamMember[]
  communications: Communication[]
  decisions: Decision[]
  resources: Resource[]
  relatedIncidents: string[]
  lessons?: string[]
}

interface TimelineEvent {
  id: string
  timestamp: string
  type: 'detection' | 'escalation' | 'action' | 'communication' | 'resolution'
  description: string
  actor: string
  metadata?: any
}

interface TeamMember {
  id: string
  name: string
  role: string
  status: 'available' | 'engaged' | 'unavailable'
  contactInfo: {
    phone: string
    email: string
    alternateContact?: string
  }
  responsibilityArea: string
  joinedAt?: string
}

interface Communication {
  id: string
  timestamp: string
  type: 'internal' | 'external' | 'stakeholder' | 'media'
  channel: 'email' | 'phone' | 'sms' | 'meeting' | 'announcement'
  from: string
  to: string[]
  subject: string
  content: string
  status: 'draft' | 'sent' | 'delivered' | 'failed'
}

interface Decision {
  id: string
  timestamp: string
  madeBy: string
  approvedBy?: string[]
  title: string
  description: string
  impact: 'high' | 'medium' | 'low'
  category: 'strategic' | 'tactical' | 'operational'
  outcome?: string
}

interface Resource {
  id: string
  name: string
  type: 'personnel' | 'equipment' | 'facility' | 'service' | 'financial'
  status: 'available' | 'allocated' | 'depleted'
  quantity?: number
  allocatedAt?: string
  cost?: number
}

interface IncidentMetrics {
  totalIncidents: number
  activeIncidents: number
  resolvedToday: number
  averageResolutionTime: number
  criticalIncidents: number
  complianceRate: number
  teamReadiness: number
  communicationEffectiveness: number
}

// Mock data generator
const generateMockIncidents = (): Incident[] => {
  return [
    {
      id: 'INC-2024-001',
      title: 'Data Center Power Outage',
      description: 'Complete power failure in primary data center affecting critical services',
      severity: 'critical',
      status: 'responding',
      type: 'operational',
      detectedAt: '2024-01-15T09:30:00Z',
      reportedBy: 'NOC Team',
      assignedTo: ['john.doe', 'jane.smith'],
      impactedAreas: ['IT Services', 'Customer Portal', 'Internal Systems'],
      estimatedRTO: 240,
      estimatedRecoveryCost: 50000,
      timeline: [
        {
          id: 'TL001',
          timestamp: '2024-01-15T09:30:00Z',
          type: 'detection',
          description: 'Power outage detected by monitoring system',
          actor: 'Monitoring System'
        },
        {
          id: 'TL002',
          timestamp: '2024-01-15T09:35:00Z',
          type: 'escalation',
          description: 'Incident escalated to Crisis Management Team',
          actor: 'NOC Supervisor'
        },
        {
          id: 'TL003',
          timestamp: '2024-01-15T09:45:00Z',
          type: 'action',
          description: 'Backup generators activated',
          actor: 'Facility Team'
        }
      ],
      responseTeam: [
        {
          id: 'TM001',
          name: 'John Doe',
          role: 'Incident Commander',
          status: 'engaged',
          contactInfo: {
            phone: '+1-555-0101',
            email: 'john.doe@company.com'
          },
          responsibilityArea: 'Overall incident coordination',
          joinedAt: '2024-01-15T09:35:00Z'
        },
        {
          id: 'TM002',
          name: 'Jane Smith',
          role: 'Technical Lead',
          status: 'engaged',
          contactInfo: {
            phone: '+1-555-0102',
            email: 'jane.smith@company.com'
          },
          responsibilityArea: 'System recovery',
          joinedAt: '2024-01-15T09:40:00Z'
        }
      ],
      communications: [
        {
          id: 'COM001',
          timestamp: '2024-01-15T09:45:00Z',
          type: 'stakeholder',
          channel: 'email',
          from: 'incident.team@company.com',
          to: ['executives@company.com'],
          subject: 'Critical Incident: Data Center Power Outage',
          content: 'We are experiencing a complete power outage...',
          status: 'delivered'
        }
      ],
      decisions: [
        {
          id: 'DEC001',
          timestamp: '2024-01-15T09:50:00Z',
          madeBy: 'John Doe',
          approvedBy: ['CEO', 'CTO'],
          title: 'Activate DR Site',
          description: 'Initiate failover to disaster recovery site',
          impact: 'high',
          category: 'strategic'
        }
      ],
      resources: [
        {
          id: 'RES001',
          name: 'Backup Generators',
          type: 'equipment',
          status: 'allocated',
          quantity: 3,
          allocatedAt: '2024-01-15T09:45:00Z'
        }
      ],
      relatedIncidents: []
    },
    {
      id: 'INC-2024-002',
      title: 'Ransomware Attack Detected',
      description: 'Suspicious encryption activity detected on file servers',
      severity: 'high',
      status: 'assessing',
      type: 'cyber',
      detectedAt: '2024-01-15T14:20:00Z',
      reportedBy: 'Security Team',
      assignedTo: ['security.lead'],
      impactedAreas: ['File Storage', 'User Workstations'],
      estimatedRTO: 480,
      estimatedRecoveryCost: 100000,
      timeline: [],
      responseTeam: [],
      communications: [],
      decisions: [],
      resources: [],
      relatedIncidents: []
    },
    {
      id: 'INC-2024-003',
      title: 'Supply Chain Disruption',
      description: 'Key supplier unable to deliver critical components',
      severity: 'medium',
      status: 'resolved',
      type: 'supply_chain',
      detectedAt: '2024-01-14T11:00:00Z',
      reportedBy: 'Procurement Team',
      assignedTo: ['procurement.manager'],
      impactedAreas: ['Production', 'Delivery Schedule'],
      estimatedRTO: 720,
      actualRTO: 650,
      estimatedRecoveryCost: 25000,
      timeline: [],
      responseTeam: [],
      communications: [],
      decisions: [],
      resources: [],
      relatedIncidents: [],
      lessons: [
        'Need to maintain larger buffer stock',
        'Implement multi-supplier strategy',
        'Improve supplier risk monitoring'
      ]
    }
  ]
}

export function IncidentManagementModule() {
  const queryClient = useQueryClient()
  const { publishEvent, subscribeToEvents } = useBCMStore()

  const [activeTab, setActiveTab] = useState<'dashboard' | 'incidents' | 'response' | 'communication' | 'recovery' | 'analysis'>('dashboard')
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null)
  const [showNewIncidentDialog, setShowNewIncidentDialog] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterSeverity, setFilterSeverity] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  // Fetch incidents
  const { data: incidents = [], isLoading: incidentsLoading } = useQuery({
    queryKey: ['incidents'],
    queryFn: async () => {
      const response = await apiClient.get('/api/incidents')
      if (response.data) {
        return response.data
      }
      return generateMockIncidents()
    }
  })

  // Calculate metrics
  const metrics: IncidentMetrics = {
    totalIncidents: incidents.length,
    activeIncidents: incidents.filter((i: Incident) =>
      ['detected', 'assessing', 'responding', 'recovering'].includes(i.status)
    ).length,
    resolvedToday: incidents.filter((i: Incident) =>
      i.status === 'resolved' &&
      new Date(i.detectedAt).toDateString() === new Date().toDateString()
    ).length,
    averageResolutionTime:
      incidents
        .filter((i: Incident) => i.actualRTO)
        .reduce((acc: number, i: Incident) => acc + (i.actualRTO || 0), 0) /
      (incidents.filter((i: Incident) => i.actualRTO).length || 1),
    criticalIncidents: incidents.filter((i: Incident) => i.severity === 'critical').length,
    complianceRate: 85, // Mock
    teamReadiness: 92, // Mock
    communicationEffectiveness: 88 // Mock
  }

  // Filter incidents
  const filteredIncidents = incidents.filter((incident: Incident) => {
    const matchesSearch = incident.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         incident.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesSeverity = filterSeverity === 'all' || incident.severity === filterSeverity
    const matchesStatus = filterStatus === 'all' || incident.status === filterStatus
    return matchesSearch && matchesSeverity && matchesStatus
  })

  // Create new incident mutation
  const createIncidentMutation = useMutation({
    mutationFn: async (data: Partial<Incident>) => {
      return apiClient.post('/api/incidents', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
      setShowNewIncidentDialog(false)
      publishEvent({
        module: 'incident-management',
        type: 'incident-created',
        data: { message: 'New incident created' }
      })
    }
  })

  // Update incident status
  const updateIncidentStatus = useMutation({
    mutationFn: async ({ id, status }: { id: string, status: string }) => {
      return apiClient.patch(`/api/incidents/${id}`, { status })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
    }
  })

  // Severity badge color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500'
      case 'high': return 'bg-orange-500'
      case 'medium': return 'bg-yellow-500'
      case 'low': return 'bg-blue-500'
      default: return 'bg-gray-500'
    }
  }

  // Status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'detected': return 'bg-red-500'
      case 'assessing': return 'bg-orange-500'
      case 'responding': return 'bg-yellow-500'
      case 'recovering': return 'bg-blue-500'
      case 'resolved': return 'bg-green-500'
      case 'closed': return 'bg-gray-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Incident Management</h1>
          <p className="text-muted-foreground mt-1">
            Monitor, respond, and recover from business disruptions
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => queryClient.invalidateQueries({ queryKey: ['incidents'] })}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Dialog open={showNewIncidentDialog} onOpenChange={setShowNewIncidentDialog}>
            <DialogTrigger asChild>
              <Button className="bg-red-600 hover:bg-red-700">
                <Siren className="w-4 h-4 mr-2" />
                Report Incident
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Report New Incident</DialogTitle>
                <DialogDescription>
                  Initiate incident response process for a new disruption
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <Label>Incident Title</Label>
                  <Input placeholder="Brief description of the incident" />
                </div>
                <div>
                  <Label>Description</Label>
                  <Textarea placeholder="Detailed description of what happened" rows={3} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Severity</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select severity" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="critical">Critical</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="low">Low</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Type</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="operational">Operational</SelectItem>
                        <SelectItem value="cyber">Cyber Security</SelectItem>
                        <SelectItem value="natural_disaster">Natural Disaster</SelectItem>
                        <SelectItem value="health_safety">Health & Safety</SelectItem>
                        <SelectItem value="supply_chain">Supply Chain</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label>Impacted Areas</Label>
                  <Input placeholder="List affected business areas (comma-separated)" />
                </div>
                <div>
                  <Label>Initial Assessment</Label>
                  <Textarea placeholder="Initial impact assessment and immediate actions taken" rows={3} />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowNewIncidentDialog(false)}>
                    Cancel
                  </Button>
                  <Button className="bg-red-600 hover:bg-red-700">
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    Report Incident
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Critical Alert */}
      {metrics.criticalIncidents > 0 && (
        <Alert className="border-red-500 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>{metrics.criticalIncidents} Critical Incident{metrics.criticalIncidents > 1 ? 's' : ''}</strong> requiring immediate attention.
            Response teams are actively engaged.
          </AlertDescription>
        </Alert>
      )}

      {/* Metrics Overview */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Incidents
              </CardTitle>
              <AlertCircle className="w-4 h-4 text-orange-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.activeIncidents}</div>
            <div className="text-xs text-muted-foreground mt-1">
              {metrics.criticalIncidents} critical
            </div>
            <Progress value={metrics.activeIncidents * 10} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Avg Resolution Time
              </CardTitle>
              <Clock className="w-4 h-4 text-blue-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(metrics.averageResolutionTime)} min</div>
            <div className="text-xs text-muted-foreground mt-1">
              Within RTO targets
            </div>
            <Progress value={75} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Team Readiness
              </CardTitle>
              <Users className="w-4 h-4 text-green-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.teamReadiness}%</div>
            <div className="text-xs text-muted-foreground mt-1">
              Personnel available
            </div>
            <Progress value={metrics.teamReadiness} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Communication
              </CardTitle>
              <MessageSquare className="w-4 h-4 text-purple-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.communicationEffectiveness}%</div>
            <div className="text-xs text-muted-foreground mt-1">
              Effectiveness rate
            </div>
            <Progress value={metrics.communicationEffectiveness} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)}>
        <TabsList className="grid grid-cols-6 w-full">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="incidents">Incidents</TabsTrigger>
          <TabsTrigger value="response">Response</TabsTrigger>
          <TabsTrigger value="communication">Communication</TabsTrigger>
          <TabsTrigger value="recovery">Recovery</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="mt-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Active Incidents List */}
            <Card>
              <CardHeader>
                <CardTitle>Active Incidents</CardTitle>
                <CardDescription>Currently ongoing incidents requiring attention</CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-3">
                    {incidents
                      .filter((i: Incident) => ['detected', 'assessing', 'responding', 'recovering'].includes(i.status))
                      .map((incident: Incident) => (
                        <div
                          key={incident.id}
                          className="border rounded-lg p-3 cursor-pointer hover:bg-accent"
                          onClick={() => setSelectedIncident(incident)}
                        >
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <div className="font-medium">{incident.title}</div>
                              <div className="text-sm text-muted-foreground">
                                {incident.id} • {new Date(incident.detectedAt).toLocaleString()}
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Badge className={getSeverityColor(incident.severity)}>
                                {incident.severity}
                              </Badge>
                              <Badge className={getStatusColor(incident.status)}>
                                {incident.status}
                              </Badge>
                            </div>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {incident.description}
                          </div>
                          <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Target className="w-3 h-3" />
                              RTO: {incident.estimatedRTO} min
                            </div>
                            <div className="flex items-center gap-1">
                              <Users className="w-3 h-3" />
                              Team: {incident.responseTeam.length}
                            </div>
                            <div className="flex items-center gap-1">
                              <MapPin className="w-3 h-3" />
                              Areas: {incident.impactedAreas.length}
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Response Team Status */}
            <Card>
              <CardHeader>
                <CardTitle>Response Team Status</CardTitle>
                <CardDescription>Current team engagement and availability</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="border rounded-lg p-3">
                      <UserCheck className="w-5 h-5 mx-auto mb-1 text-green-500" />
                      <div className="text-2xl font-bold">24</div>
                      <div className="text-xs text-muted-foreground">Available</div>
                    </div>
                    <div className="border rounded-lg p-3">
                      <Users className="w-5 h-5 mx-auto mb-1 text-yellow-500" />
                      <div className="text-2xl font-bold">8</div>
                      <div className="text-xs text-muted-foreground">Engaged</div>
                    </div>
                    <div className="border rounded-lg p-3">
                      <XCircle className="w-5 h-5 mx-auto mb-1 text-red-500" />
                      <div className="text-2xl font-bold">3</div>
                      <div className="text-xs text-muted-foreground">Unavailable</div>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <h4 className="text-sm font-medium mb-2">Key Personnel</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span className="text-sm">John Doe - Incident Commander</span>
                        </div>
                        <Badge variant="outline" className="text-xs">Available</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                          <span className="text-sm">Jane Smith - Technical Lead</span>
                        </div>
                        <Badge variant="outline" className="text-xs">Engaged</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span className="text-sm">Mike Johnson - Communications</span>
                        </div>
                        <Badge variant="outline" className="text-xs">Available</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                          <span className="text-sm">Sarah Wilson - Recovery Lead</span>
                        </div>
                        <Badge variant="outline" className="text-xs">Engaged</Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="incidents" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>All Incidents</CardTitle>
                  <CardDescription>Complete incident registry and history</CardDescription>
                </div>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search incidents..."
                      className="pl-8 w-64"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                  <Select value={filterSeverity} onValueChange={setFilterSeverity}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Severity" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Severity</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filterStatus} onValueChange={setFilterStatus}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="detected">Detected</SelectItem>
                      <SelectItem value="assessing">Assessing</SelectItem>
                      <SelectItem value="responding">Responding</SelectItem>
                      <SelectItem value="recovering">Recovering</SelectItem>
                      <SelectItem value="resolved">Resolved</SelectItem>
                      <SelectItem value="closed">Closed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="border rounded-lg">
                <table className="w-full">
                  <thead className="border-b bg-muted/50">
                    <tr>
                      <th className="text-left p-3 font-medium">Incident ID</th>
                      <th className="text-left p-3 font-medium">Title</th>
                      <th className="text-left p-3 font-medium">Severity</th>
                      <th className="text-left p-3 font-medium">Status</th>
                      <th className="text-left p-3 font-medium">Type</th>
                      <th className="text-left p-3 font-medium">Detected</th>
                      <th className="text-left p-3 font-medium">RTO</th>
                      <th className="text-left p-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredIncidents.map((incident: Incident) => (
                      <tr key={incident.id} className="border-b hover:bg-accent">
                        <td className="p-3 font-mono text-sm">{incident.id}</td>
                        <td className="p-3">
                          <div>
                            <div className="font-medium">{incident.title}</div>
                            <div className="text-xs text-muted-foreground">
                              {incident.impactedAreas.join(', ')}
                            </div>
                          </div>
                        </td>
                        <td className="p-3">
                          <Badge className={getSeverityColor(incident.severity)}>
                            {incident.severity}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <Badge className={getStatusColor(incident.status)}>
                            {incident.status}
                          </Badge>
                        </td>
                        <td className="p-3 capitalize">{incident.type.replace('_', ' ')}</td>
                        <td className="p-3 text-sm">
                          {new Date(incident.detectedAt).toLocaleString()}
                        </td>
                        <td className="p-3">
                          <div className="text-sm">
                            <div>{incident.estimatedRTO} min</div>
                            {incident.actualRTO && (
                              <div className="text-xs text-muted-foreground">
                                Actual: {incident.actualRTO} min
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="p-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedIncident(incident)}
                          >
                            View
                            <ChevronRight className="w-4 h-4 ml-1" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="response" className="mt-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Response Procedures */}
            <Card>
              <CardHeader>
                <CardTitle>Response Procedures</CardTitle>
                <CardDescription>Standardized incident response workflows</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="border rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="w-4 h-4 text-blue-500" />
                      <span className="font-medium">Initial Response</span>
                    </div>
                    <div className="space-y-1 text-sm text-muted-foreground pl-6">
                      <div>1. Activate incident response team</div>
                      <div>2. Assess initial impact and scope</div>
                      <div>3. Implement immediate containment</div>
                      <div>4. Notify stakeholders</div>
                    </div>
                  </div>
                  <div className="border rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Zap className="w-4 h-4 text-yellow-500" />
                      <span className="font-medium">Escalation Criteria</span>
                    </div>
                    <div className="space-y-1 text-sm text-muted-foreground pl-6">
                      <div>• Critical system failure {'>'}30 mins</div>
                      <div>• Data breach confirmed</div>
                      <div>• Safety incident with injuries</div>
                      <div>• Media attention expected</div>
                    </div>
                  </div>
                  <div className="border rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Activity className="w-4 h-4 text-green-500" />
                      <span className="font-medium">Recovery Actions</span>
                    </div>
                    <div className="space-y-1 text-sm text-muted-foreground pl-6">
                      <div>1. Implement recovery plan</div>
                      <div>2. Monitor system restoration</div>
                      <div>3. Validate functionality</div>
                      <div>4. Document lessons learned</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Response Resources */}
            <Card>
              <CardHeader>
                <CardTitle>Response Resources</CardTitle>
                <CardDescription>Available resources for incident response</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Personnel</span>
                      <Badge variant="outline">24 Available</Badge>
                    </div>
                    <Progress value={80} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Equipment</span>
                      <Badge variant="outline">Ready</Badge>
                    </div>
                    <Progress value={100} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Facilities</span>
                      <Badge variant="outline">3 Sites</Badge>
                    </div>
                    <Progress value={100} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Communication Channels</span>
                      <Badge variant="outline">Active</Badge>
                    </div>
                    <Progress value={95} className="h-2" />
                  </div>
                  <Separator className="my-4" />
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Quick Actions</h4>
                    <div className="grid grid-cols-2 gap-2">
                      <Button size="sm" variant="outline">
                        <PhoneCall className="w-4 h-4 mr-2" />
                        Call Tree
                      </Button>
                      <Button size="sm" variant="outline">
                        <Users className="w-4 h-4 mr-2" />
                        Team Assembly
                      </Button>
                      <Button size="sm" variant="outline">
                        <FileText className="w-4 h-4 mr-2" />
                        Templates
                      </Button>
                      <Button size="sm" variant="outline">
                        <Bell className="w-4 h-4 mr-2" />
                        Mass Notify
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="communication" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Crisis Communication</CardTitle>
              <CardDescription>Manage internal and external communications during incidents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Communication Templates */}
                <div>
                  <h3 className="text-lg font-medium mb-3">Communication Templates</h3>
                  <div className="grid grid-cols-3 gap-3">
                    <Button variant="outline" className="justify-start">
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Initial Notification
                    </Button>
                    <Button variant="outline" className="justify-start">
                      <Users className="w-4 h-4 mr-2" />
                      Stakeholder Update
                    </Button>
                    <Button variant="outline" className="justify-start">
                      <FileText className="w-4 h-4 mr-2" />
                      Media Statement
                    </Button>
                    <Button variant="outline" className="justify-start">
                      <Bell className="w-4 h-4 mr-2" />
                      Employee Alert
                    </Button>
                    <Button variant="outline" className="justify-start">
                      <Target className="w-4 h-4 mr-2" />
                      Customer Notice
                    </Button>
                    <Button variant="outline" className="justify-start">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Resolution Notice
                    </Button>
                  </div>
                </div>

                {/* Recent Communications */}
                <div>
                  <h3 className="text-lg font-medium mb-3">Recent Communications</h3>
                  <div className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium">Stakeholder Update Sent</div>
                            <div className="text-sm text-muted-foreground">
                              To: Executive Team, Board Members
                            </div>
                          </div>
                          <span className="text-xs text-muted-foreground">10 mins ago</span>
                        </div>
                      </div>
                    </div>
                    <Separator />
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium">Employee Alert Broadcast</div>
                            <div className="text-sm text-muted-foreground">
                              To: All Staff
                            </div>
                          </div>
                          <span className="text-xs text-muted-foreground">25 mins ago</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recovery" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Recovery Operations</CardTitle>
              <CardDescription>Track and manage recovery efforts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Recovery Progress */}
                <div>
                  <h3 className="text-lg font-medium mb-3">Recovery Progress</h3>
                  <div className="space-y-3">
                    <div className="border rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium">System Restoration</span>
                        <span className="text-sm text-muted-foreground">75% Complete</span>
                      </div>
                      <Progress value={75} className="h-2 mb-2" />
                      <div className="text-xs text-muted-foreground">
                        Estimated completion: 2 hours
                      </div>
                    </div>
                    <div className="border rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium">Data Recovery</span>
                        <span className="text-sm text-muted-foreground">100% Complete</span>
                      </div>
                      <Progress value={100} className="h-2 mb-2" />
                      <div className="text-xs text-green-600">
                        All data successfully recovered
                      </div>
                    </div>
                    <div className="border rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium">Service Validation</span>
                        <span className="text-sm text-muted-foreground">In Progress</span>
                      </div>
                      <Progress value={40} className="h-2 mb-2" />
                      <div className="text-xs text-muted-foreground">
                        Testing critical functions
                      </div>
                    </div>
                  </div>
                </div>

                {/* Recovery Checklist */}
                <div>
                  <h3 className="text-lg font-medium mb-3">Recovery Checklist</h3>
                  <div className="space-y-2">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" className="rounded" defaultChecked />
                      <span>Backup systems activated</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" className="rounded" defaultChecked />
                      <span>Data integrity verified</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" className="rounded" />
                      <span>User access restored</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" className="rounded" />
                      <span>Performance benchmarks met</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" className="rounded" />
                      <span>Stakeholder sign-off received</span>
                    </label>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="mt-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Incident Trends */}
            <Card>
              <CardHeader>
                <CardTitle>Incident Trends</CardTitle>
                <CardDescription>Analysis of incident patterns over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">By Severity</span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <div className="w-20 text-sm">Critical</div>
                        <Progress value={15} className="flex-1 h-2" />
                        <span className="text-sm w-10">15%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-20 text-sm">High</div>
                        <Progress value={30} className="flex-1 h-2" />
                        <span className="text-sm w-10">30%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-20 text-sm">Medium</div>
                        <Progress value={40} className="flex-1 h-2" />
                        <span className="text-sm w-10">40%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-20 text-sm">Low</div>
                        <Progress value={15} className="flex-1 h-2" />
                        <span className="text-sm w-10">15%</span>
                      </div>
                    </div>
                  </div>
                  <Separator />
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">By Type</span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <div className="w-20 text-sm">Operational</div>
                        <Progress value={45} className="flex-1 h-2" />
                        <span className="text-sm w-10">45%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-20 text-sm">Cyber</div>
                        <Progress value={25} className="flex-1 h-2" />
                        <span className="text-sm w-10">25%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-20 text-sm">Supply</div>
                        <Progress value={20} className="flex-1 h-2" />
                        <span className="text-sm w-10">20%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-20 text-sm">Other</div>
                        <Progress value={10} className="flex-1 h-2" />
                        <span className="text-sm w-10">10%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Lessons Learned */}
            <Card>
              <CardHeader>
                <CardTitle>Lessons Learned</CardTitle>
                <CardDescription>Key insights from resolved incidents</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="border rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <TrendingUp className="w-4 h-4 mt-0.5 text-green-500" />
                      <div>
                        <div className="font-medium text-sm">Improved Response Time</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Automated alerting reduced initial response by 40%
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="border rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <Shield className="w-4 h-4 mt-0.5 text-blue-500" />
                      <div>
                        <div className="font-medium text-sm">Enhanced Security Measures</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Multi-factor authentication prevented unauthorized access
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="border rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <Users className="w-4 h-4 mt-0.5 text-purple-500" />
                      <div>
                        <div className="font-medium text-sm">Team Coordination</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Regular drills improved team response effectiveness by 60%
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="border rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <Target className="w-4 h-4 mt-0.5 text-orange-500" />
                      <div>
                        <div className="font-medium text-sm">RTO Achievement</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          90% of incidents resolved within target recovery time
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Selected Incident Detail Modal */}
      {selectedIncident && (
        <Dialog open={!!selectedIncident} onOpenChange={() => setSelectedIncident(null)}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <div className="flex justify-between items-start">
                <div>
                  <DialogTitle className="text-xl">{selectedIncident.title}</DialogTitle>
                  <DialogDescription>{selectedIncident.id}</DialogDescription>
                </div>
                <div className="flex gap-2">
                  <Badge className={getSeverityColor(selectedIncident.severity)}>
                    {selectedIncident.severity}
                  </Badge>
                  <Badge className={getStatusColor(selectedIncident.status)}>
                    {selectedIncident.status}
                  </Badge>
                </div>
              </div>
            </DialogHeader>
            <div className="space-y-6 mt-6">
              {/* Incident Details */}
              <div>
                <h3 className="font-medium mb-2">Incident Details</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Type:</span>
                    <span className="capitalize">{selectedIncident.type.replace('_', ' ')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Detected:</span>
                    <span>{new Date(selectedIncident.detectedAt).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Reported By:</span>
                    <span>{selectedIncident.reportedBy}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Estimated RTO:</span>
                    <span>{selectedIncident.estimatedRTO} minutes</span>
                  </div>
                  {selectedIncident.actualRTO && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Actual RTO:</span>
                      <span>{selectedIncident.actualRTO} minutes</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Impacted Areas */}
              <div>
                <h3 className="font-medium mb-2">Impacted Areas</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedIncident.impactedAreas.map((area, i) => (
                    <Badge key={i} variant="outline">{area}</Badge>
                  ))}
                </div>
              </div>

              {/* Timeline */}
              {selectedIncident.timeline.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Timeline</h3>
                  <div className="space-y-2">
                    {selectedIncident.timeline.map((event) => (
                      <div key={event.id} className="flex items-start gap-3 text-sm">
                        <div className="text-muted-foreground w-20">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </div>
                        <div className="flex-1">
                          <div>{event.description}</div>
                          <div className="text-xs text-muted-foreground">{event.actor}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Response Team */}
              {selectedIncident.responseTeam.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Response Team</h3>
                  <div className="space-y-2">
                    {selectedIncident.responseTeam.map((member) => (
                      <div key={member.id} className="flex justify-between items-center">
                        <div>
                          <div className="font-medium text-sm">{member.name}</div>
                          <div className="text-xs text-muted-foreground">{member.role}</div>
                        </div>
                        <Badge
                          variant="outline"
                          className={
                            member.status === 'engaged' ? 'border-yellow-500' :
                            member.status === 'available' ? 'border-green-500' :
                            'border-red-500'
                          }
                        >
                          {member.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Lessons Learned */}
              {selectedIncident.lessons && selectedIncident.lessons.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Lessons Learned</h3>
                  <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                    {selectedIncident.lessons.map((lesson, i) => (
                      <li key={i}>{lesson}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}