'use client'

import { useState } from 'react'
import { CreateProcessForm } from '@/components/forms/CreateProcessForm'
import { useProcesses, useDeleteProcess, useArchiveProcess } from '@/lib/hooks/useWorkflow'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { SectionTabContent, SectionHeader } from '@/components/sections/SectionLayout'
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Edit,
  Trash2,
  Play,
  Pause,
  Clock,
  Users,
  CheckCircle,
  AlertTriangle,
  FileText,
  Settings,
  GitBranch,
  Activity,
  Eye,
  Archive,
  Loader2
} from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface BusinessProcess {
  id: string
  name: string
  description: string
  category: 'bcp' | 'incident' | 'training' | 'audit' | 'governance'
  status: 'active' | 'draft' | 'archived' | 'under_review'
  owner: string
  department: string
  lastModified: string
  version: string
  stakeholders: string[]
  complexity: 'low' | 'medium' | 'high'
  criticality: 'low' | 'medium' | 'high' | 'critical'
  rto: string // Recovery Time Objective
  rpo: string // Recovery Point Objective
}

interface ProcessTemplate {
  id: string
  name: string
  description: string
  category: string
  elements: number
  useCount: number
}

// Mock data
const mockProcesses: BusinessProcess[] = [
  {
    id: '1',
    name: 'Emergency Response Protocol',
    description: 'Comprehensive emergency response and crisis management process',
    category: 'incident',
    status: 'active',
    owner: 'John Smith',
    department: 'Security',
    lastModified: '2024-01-15',
    version: '2.1',
    stakeholders: ['Security Team', 'Management', 'IT Support'],
    complexity: 'high',
    criticality: 'critical',
    rto: '15 minutes',
    rpo: '5 minutes'
  },
  {
    id: '2',
    name: 'Business Continuity Plan Review',
    description: 'Quarterly review and update process for business continuity plans',
    category: 'bcp',
    status: 'active',
    owner: 'Sarah Johnson',
    department: 'Risk Management',
    lastModified: '2024-01-12',
    version: '1.3',
    stakeholders: ['Risk Team', 'Department Heads', 'External Auditors'],
    complexity: 'medium',
    criticality: 'high',
    rto: '4 hours',
    rpo: '1 hour'
  },
  {
    id: '3',
    name: 'Staff Training Compliance',
    description: 'Process for ensuring all staff complete required BCM training',
    category: 'training',
    status: 'under_review',
    owner: 'Mike Davis',
    department: 'HR',
    lastModified: '2024-01-10',
    version: '1.0',
    stakeholders: ['HR Team', 'Training Coordinators', 'Department Managers'],
    complexity: 'low',
    criticality: 'medium',
    rto: '24 hours',
    rpo: '4 hours'
  },
  {
    id: '4',
    name: 'Audit Preparation Workflow',
    description: 'Internal audit preparation and documentation process',
    category: 'audit',
    status: 'draft',
    owner: 'Lisa Wilson',
    department: 'Compliance',
    lastModified: '2024-01-08',
    version: '0.5',
    stakeholders: ['Compliance Team', 'Internal Auditors'],
    complexity: 'medium',
    criticality: 'medium',
    rto: '8 hours',
    rpo: '2 hours'
  }
]

const mockTemplates: ProcessTemplate[] = [
  {
    id: '1',
    name: 'Incident Response Template',
    description: 'Standard template for incident response workflows',
    category: 'Incident Management',
    elements: 12,
    useCount: 25
  },
  {
    id: '2',
    name: 'BCP Review Template',
    description: 'Template for business continuity plan review processes',
    category: 'Planning',
    elements: 8,
    useCount: 18
  },
  {
    id: '3',
    name: 'Training Workflow Template',
    description: 'Template for training completion and tracking workflows',
    category: 'Training',
    elements: 6,
    useCount: 12
  }
]

function getStatusColor(status: string) {
  switch (status) {
    case 'active': return 'bg-green-100 text-green-700'
    case 'draft': return 'bg-gray-100 text-gray-700'
    case 'archived': return 'bg-blue-100 text-blue-700'
    case 'under_review': return 'bg-yellow-100 text-yellow-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

function getCriticalityColor(criticality: string) {
  switch (criticality) {
    case 'critical': return 'bg-red-100 text-red-700'
    case 'high': return 'bg-orange-100 text-orange-700'
    case 'medium': return 'bg-yellow-100 text-yellow-700'
    case 'low': return 'bg-green-100 text-green-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

function getCategoryIcon(category: string) {
  switch (category) {
    case 'incident': return <AlertTriangle className="h-4 w-4" />
    case 'bcp': return <FileText className="h-4 w-4" />
    case 'training': return <Users className="h-4 w-4" />
    case 'audit': return <CheckCircle className="h-4 w-4" />
    case 'governance': return <Settings className="h-4 w-4" />
    default: return <Activity className="h-4 w-4" />
  }
}

export function ProcessManagement() {
  const [selectedProcess, setSelectedProcess] = useState<BusinessProcess | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)

  // Use real API hooks
  const {
    data: processesData,
    isLoading,
    error,
    refetch
  } = useProcesses({
    category: filterCategory === 'all' ? undefined : filterCategory,
    status: filterStatus === 'all' ? undefined : filterStatus,
    search: searchTerm || undefined,
    page: currentPage,
    limit: 20
  })

  const deleteProcess = useDeleteProcess()
  const archiveProcess = useArchiveProcess()

  const processes = processesData?.data || []
  const pagination = processesData?.pagination

  const handleCreateProcess = () => {
    setIsCreateDialogOpen(true)
  }

  const handleEditProcess = (process: BusinessProcess) => {
    setSelectedProcess(process)
    console.log('Editing process:', process.name)
  }

  const handleDeleteProcess = async (processId: string) => {
    if (confirm('Are you sure you want to delete this process? This action cannot be undone.')) {
      await deleteProcess.mutateAsync(processId)
    }
  }

  const handleArchiveProcess = async (processId: string) => {
    await archiveProcess.mutateAsync(processId)
  }

  const handleProcessCreated = () => {
    setIsCreateDialogOpen(false)
    refetch() // Refresh the list
  }

  return (
    <SectionTabContent>
      <SectionHeader
        title="Process Management"
        description="Manage and monitor business continuity processes and workflows"
      >
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button onClick={handleCreateProcess}>
            <Plus className="h-4 w-4 mr-2" />
            New Process
          </Button>
        </div>
      </SectionHeader>

      <Tabs defaultValue="processes" className="space-y-6">
        <TabsList>
          <TabsTrigger value="processes">Active Processes</TabsTrigger>
          <TabsTrigger value="templates">Process Templates</TabsTrigger>
          <TabsTrigger value="analytics">Process Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="processes" className="space-y-6">
          {/* Search and Filter */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="Search processes..."
                      value={searchTerm}
                      onChange={(e) => {
                        setSearchTerm(e.target.value)
                        setCurrentPage(1) // Reset to first page on search
                      }}
                      className="pl-10"
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Select value={filterCategory} onValueChange={setFilterCategory}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      <SelectItem value="incident">Incident</SelectItem>
                      <SelectItem value="bcp">BCP</SelectItem>
                      <SelectItem value="training">Training</SelectItem>
                      <SelectItem value="audit">Audit</SelectItem>
                      <SelectItem value="governance">Governance</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filterStatus} onValueChange={setFilterStatus}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="under_review">Under Review</SelectItem>
                      <SelectItem value="archived">Archived</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Loading State */}
          {isLoading && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-center py-8">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Loading processes...</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Error State */}
          {error && (
            <Card>
              <CardContent className="pt-6">
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    Failed to load processes: {error.message}
                    <Button variant="outline" size="sm" onClick={() => refetch()} className="ml-2">
                      Retry
                    </Button>
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          )}

          {/* Process List */}
          {!isLoading && !error && (
            <Card>
              <CardHeader>
                <CardTitle>
                  Business Processes ({pagination?.total || 0})
                  {isLoading && <Loader2 className="ml-2 h-4 w-4 animate-spin inline" />}
                </CardTitle>
                <CardDescription>
                  Manage your business continuity processes and workflows
                  {pagination && (
                    <span className="ml-2">
                      (Page {pagination.page} of {pagination.totalPages})
                    </span>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Process</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Owner</TableHead>
                    <TableHead>Criticality</TableHead>
                    <TableHead>RTO/RPO</TableHead>
                    <TableHead>Modified</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {processes.map((process) => (
                    <TableRow key={process.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{process.name}</div>
                          <div className="text-sm text-gray-500">{process.description}</div>
                          <div className="flex items-center mt-1 space-x-2">
                            <Badge variant="outline" className="text-xs">
                              v{process.version}
                            </Badge>
                            <span className="text-xs text-gray-400">
                              {process.stakeholders.length} stakeholders
                            </span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {getCategoryIcon(process.category)}
                          <span className="capitalize">{process.category}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="secondary"
                          className={getStatusColor(process.status)}
                        >
                          {process.status.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{process.owner}</div>
                          <div className="text-sm text-gray-500">{process.department}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="secondary"
                          className={getCriticalityColor(process.criticality)}
                        >
                          {process.criticality}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>RTO: {process.rto}</div>
                          <div>RPO: {process.rpo}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm text-gray-500">
                          {process.lastModified}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => console.log('Viewing process:', process.name)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditProcess(process)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleArchiveProcess(process.id)}
                          >
                            <Archive className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteProcess(process.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="templates" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Process Templates</CardTitle>
              <CardDescription>
                Pre-built templates to quickly create new processes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {mockTemplates.map((template) => (
                  <Card key={template.id} className="cursor-pointer hover:shadow-md transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                      <CardDescription>{template.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Category:</span>
                          <span>{template.category}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Elements:</span>
                          <span>{template.elements}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Used:</span>
                          <span>{template.useCount} times</span>
                        </div>
                        <div className="mt-4">
                          <Button className="w-full" size="sm">
                            Use Template
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Processes</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{processes.length}</div>
                <p className="text-xs text-muted-foreground">+2 from last month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Processes</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {processes.filter(p => p.status === 'active').length}
                </div>
                <p className="text-xs text-muted-foreground">+1 from last week</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Critical Processes</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {processes.filter(p => p.criticality === 'critical').length}
                </div>
                <p className="text-xs text-muted-foreground">No change</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg. RTO</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">2.5h</div>
                <p className="text-xs text-muted-foreground">-0.5h improvement</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Process Distribution</CardTitle>
              <CardDescription>
                Breakdown of processes by category and status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">By Category</h4>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    {['incident', 'bcp', 'training', 'audit', 'governance'].map(category => {
                      const count = processes.filter(p => p.category === category).length
                      return (
                        <div key={category} className="text-center">
                          <div className="text-2xl font-bold">{count}</div>
                          <div className="text-sm text-gray-500 capitalize">{category}</div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2">By Status</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {['active', 'draft', 'under_review', 'archived'].map(status => {
                      const count = processes.filter(p => p.status === status).length
                      return (
                        <div key={status} className="text-center">
                          <div className="text-2xl font-bold">{count}</div>
                          <div className="text-sm text-gray-500 capitalize">
                            {status.replace('_', ' ')}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Process Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Business Process</DialogTitle>
            <DialogDescription>
              Define a new business continuity process with full validation
            </DialogDescription>
          </DialogHeader>
          <CreateProcessForm
            onSuccess={handleProcessCreated}
            onCancel={() => setIsCreateDialogOpen(false)}
            enableWorkflowCreation={false}
          />
        </DialogContent>
      </Dialog>
    </SectionTabContent>
  )
}