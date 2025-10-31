'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useBCMStore } from '@/lib/store'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Progress } from '@/components/ui/progress'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import {
  Target,
  Play,
  Pause,
  Square,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Users,
  Calendar as CalendarIcon,
  FileText,
  Settings,
  BarChart3,
  TrendingUp,
  Plus,
  Search,
  Filter,
  Edit,
  Eye,
  Copy,
  Download,
  Upload,
  Send,
  Award,
  Lightbulb,
  Shield,
  Zap,
  Globe
} from 'lucide-react'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'

// Types
interface ExerciseObjective {
  id: string
  description: string
  success_criteria: string
  priority: 'high' | 'medium' | 'low'
  achieved?: boolean
  notes?: string
}

interface ExerciseParticipant {
  id: string
  name: string
  role: string
  department: string
  email: string
  participation_type: 'observer' | 'player' | 'controller' | 'evaluator'
  attendance_status: 'confirmed' | 'tentative' | 'declined' | 'no_response'
  performance_rating?: number
  feedback?: string
}

interface ExerciseScenario {
  id: string
  title: string
  description: string
  threat_type: 'cyber_attack' | 'natural_disaster' | 'pandemic' | 'supply_chain' | 'facility_damage' | 'key_personnel' | 'technology_failure'
  severity_level: 'low' | 'medium' | 'high' | 'critical'
  affected_systems: string[]
  timeline: {
    time: string
    event: string
    inject_type: 'initial' | 'escalation' | 'new_information' | 'complication' | 'resolution'
  }[]
  expected_responses: string[]
  evaluation_criteria: string[]
}

interface ExerciseObservation {
  id: string
  observer: string
  timestamp: string
  category: 'strength' | 'gap' | 'improvement' | 'note'
  description: string
  severity?: 'low' | 'medium' | 'high' | 'critical'
  recommendation?: string
  responsible_party?: string
  follow_up_required: boolean
}

interface Exercise {
  id: string
  name: string
  description: string
  type: 'tabletop' | 'functional' | 'full_scale' | 'walkthrough' | 'drill'
  status: 'planning' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'postponed'

  // Scheduling
  scheduled_date: string
  start_time: string
  end_time: string
  duration_minutes: number
  location: string
  facilitator: string

  // Exercise Design
  objectives: ExerciseObjective[]
  scenario: ExerciseScenario
  participants: ExerciseParticipant[]

  // Scope and Focus
  scope: string[]
  focus_areas: string[]
  systems_tested: string[]
  plans_tested: string[]

  // Evaluation
  observations: ExerciseObservation[]
  lessons_learned: string[]
  action_items: {
    id: string
    description: string
    responsible: string
    due_date: string
    status: 'open' | 'in_progress' | 'completed'
    priority: 'high' | 'medium' | 'low'
  }[]

  // Results
  overall_rating: 'excellent' | 'good' | 'satisfactory' | 'needs_improvement' | 'poor'
  success_percentage: number
  key_findings: string[]
  recommendations: string[]

  // Metadata
  exercise_controller: string
  evaluators: string[]
  created_by: string
  created_date: string
  last_modified: string
  tags: string[]
  cost: number
  participant_feedback_summary?: {
    average_rating: number
    response_rate: number
    key_comments: string[]
  }
}

interface ExerciseProgram {
  id: string
  name: string
  description: string
  year: number
  objectives: string[]
  schedule: {
    quarter: 1 | 2 | 3 | 4
    exercises: Exercise[]
    milestones: {
      date: string
      title: string
      description: string
    }[]
  }[]
  budget: number
  resource_requirements: string[]
  success_metrics: string[]
  status: 'planning' | 'active' | 'completed'
}

// Mock Data
const generateMockExercises = (): Exercise[] => [
  {
    id: 'exercise-001',
    name: 'Cyber Incident Response Exercise 2024',
    description: 'Comprehensive exercise testing organizational response to a major cybersecurity incident',
    type: 'tabletop',
    status: 'completed',
    scheduled_date: '2024-10-15',
    start_time: '09:00',
    end_time: '16:00',
    duration_minutes: 420,
    location: 'Executive Conference Room',
    facilitator: 'Sarah Johnson',
    objectives: [
      {
        id: 'obj-001',
        description: 'Test incident response team coordination',
        success_criteria: 'Team assembles within 30 minutes and establishes command structure',
        priority: 'high',
        achieved: true
      },
      {
        id: 'obj-002',
        description: 'Evaluate communication protocols',
        success_criteria: 'All stakeholders receive timely and accurate updates',
        priority: 'high',
        achieved: true
      },
      {
        id: 'obj-003',
        description: 'Test decision-making processes',
        success_criteria: 'Critical decisions made within established timeframes',
        priority: 'medium',
        achieved: false,
        notes: 'Decision delays observed during escalation phase'
      }
    ],
    scenario: {
      id: 'scenario-001',
      title: 'Advanced Persistent Threat Campaign',
      description: 'Sophisticated cyber attack targeting customer data and financial systems',
      threat_type: 'cyber_attack',
      severity_level: 'critical',
      affected_systems: ['Customer Database', 'Payment Processing', 'Email Systems', 'File Servers'],
      timeline: [
        {
          time: '09:00',
          event: 'Unusual network activity detected by security tools',
          inject_type: 'initial'
        },
        {
          time: '10:30',
          event: 'Confirmed data exfiltration from customer database',
          inject_type: 'escalation'
        },
        {
          time: '12:00',
          event: 'Media inquiry received about potential data breach',
          inject_type: 'complication'
        },
        {
          time: '14:00',
          event: 'Regulatory notification requirement triggered',
          inject_type: 'new_information'
        }
      ],
      expected_responses: [
        'Activate incident response team',
        'Isolate affected systems',
        'Conduct damage assessment',
        'Notify stakeholders',
        'Engage external resources'
      ],
      evaluation_criteria: [
        'Response time to initial detection',
        'Effectiveness of containment measures',
        'Quality of communications',
        'Compliance with regulatory requirements'
      ]
    },
    participants: [
      {
        id: 'participant-001',
        name: 'Michael Chen',
        role: 'CTO',
        department: 'Technology',
        email: 'michael.chen@company.com',
        participation_type: 'player',
        attendance_status: 'confirmed',
        performance_rating: 4.2
      },
      {
        id: 'participant-002',
        name: 'Lisa Wang',
        role: 'CISO',
        department: 'Security',
        email: 'lisa.wang@company.com',
        participation_type: 'player',
        attendance_status: 'confirmed',
        performance_rating: 4.5
      },
      {
        id: 'participant-003',
        name: 'David Brown',
        role: 'Communications Director',
        department: 'Communications',
        email: 'david.brown@company.com',
        participation_type: 'player',
        attendance_status: 'confirmed',
        performance_rating: 3.8
      }
    ],
    scope: ['Incident Response', 'Crisis Communication', 'Stakeholder Management'],
    focus_areas: ['Cybersecurity', 'Data Protection', 'Regulatory Compliance'],
    systems_tested: ['SIEM', 'Incident Management Platform', 'Communication Systems'],
    plans_tested: ['Cyber Incident Response Plan', 'Crisis Communication Plan'],
    observations: [
      {
        id: 'obs-001',
        observer: 'John Smith',
        timestamp: '2024-10-15T10:45:00Z',
        category: 'strength',
        description: 'Excellent initial response and team coordination',
        follow_up_required: false
      },
      {
        id: 'obs-002',
        observer: 'Jane Doe',
        timestamp: '2024-10-15T12:15:00Z',
        category: 'gap',
        description: 'Delay in executive notification during escalation',
        severity: 'medium',
        recommendation: 'Review and update escalation procedures',
        responsible_party: 'BCM Manager',
        follow_up_required: true
      }
    ],
    lessons_learned: [
      'Team coordination was excellent and demonstrated strong preparedness',
      'Communication protocols need refinement for executive escalation',
      'External vendor contact procedures require updating',
      'Decision-making authority needs clearer definition for after-hours scenarios'
    ],
    action_items: [
      {
        id: 'action-001',
        description: 'Update executive escalation procedures',
        responsible: 'BCM Manager',
        due_date: '2024-11-15',
        status: 'in_progress',
        priority: 'high'
      },
      {
        id: 'action-002',
        description: 'Refresh vendor contact database',
        responsible: 'IT Manager',
        due_date: '2024-12-01',
        status: 'open',
        priority: 'medium'
      }
    ],
    overall_rating: 'good',
    success_percentage: 82,
    key_findings: [
      'Strong technical response capabilities',
      'Communication gaps during escalation',
      'Need for clearer decision authority'
    ],
    recommendations: [
      'Conduct quarterly mini-exercises to maintain readiness',
      'Develop executive decision-making playbook',
      'Enhance vendor management procedures'
    ],
    exercise_controller: 'Sarah Johnson',
    evaluators: ['John Smith', 'Jane Doe', 'Bob Wilson'],
    created_by: 'Sarah Johnson',
    created_date: '2024-09-01',
    last_modified: '2024-10-20',
    tags: ['Cybersecurity', 'Critical', 'Annual'],
    cost: 15000,
    participant_feedback_summary: {
      average_rating: 4.1,
      response_rate: 85,
      key_comments: ['Very realistic scenario', 'Good learning opportunity', 'Could use more technical details']
    }
  },
  {
    id: 'exercise-002',
    name: 'Supply Chain Disruption Exercise',
    description: 'Testing response to major supply chain disruption affecting critical operations',
    type: 'functional',
    status: 'scheduled',
    scheduled_date: '2024-12-10',
    start_time: '08:00',
    end_time: '17:00',
    duration_minutes: 540,
    location: 'Operations Center',
    facilitator: 'Michael Chen',
    objectives: [
      {
        id: 'obj-004',
        description: 'Test supplier alternative identification',
        success_criteria: 'Alternative suppliers identified within 4 hours',
        priority: 'high'
      },
      {
        id: 'obj-005',
        description: 'Evaluate customer communication',
        success_criteria: 'All customers notified within 6 hours',
        priority: 'medium'
      }
    ],
    scenario: {
      id: 'scenario-002',
      title: 'Critical Supplier Facility Fire',
      description: 'Major fire at primary supplier facility affecting 60% of critical components',
      threat_type: 'supply_chain',
      severity_level: 'high',
      affected_systems: ['Manufacturing', 'Inventory Management', 'Customer Orders'],
      timeline: [
        {
          time: '08:00',
          event: 'Notification received of supplier facility fire',
          inject_type: 'initial'
        },
        {
          time: '10:00',
          event: 'Supplier confirms 60% capacity loss for 4-6 weeks',
          inject_type: 'escalation'
        },
        {
          time: '13:00',
          event: 'Key customer threatens contract cancellation',
          inject_type: 'complication'
        }
      ],
      expected_responses: [
        'Assess impact on operations',
        'Activate supplier contingency plans',
        'Communicate with customers',
        'Implement conservation measures'
      ],
      evaluation_criteria: [
        'Speed of impact assessment',
        'Effectiveness of alternative sourcing',
        'Quality of customer communications',
        'Resource optimization decisions'
      ]
    },
    participants: [
      {
        id: 'participant-004',
        name: 'Operations Manager',
        role: 'Operations Manager',
        department: 'Operations',
        email: 'ops.manager@company.com',
        participation_type: 'player',
        attendance_status: 'confirmed'
      },
      {
        id: 'participant-005',
        name: 'Supply Chain Director',
        role: 'Supply Chain Director',
        department: 'Supply Chain',
        email: 'sc.director@company.com',
        participation_type: 'player',
        attendance_status: 'tentative'
      }
    ],
    scope: ['Supply Chain Management', 'Customer Relations', 'Operations Continuity'],
    focus_areas: ['Supplier Risk', 'Alternative Sourcing', 'Customer Communication'],
    systems_tested: ['ERP System', 'Supplier Portal', 'Customer Management'],
    plans_tested: ['Supply Chain Continuity Plan', 'Customer Communication Plan'],
    observations: [],
    lessons_learned: [],
    action_items: [],
    overall_rating: 'satisfactory',
    success_percentage: 0,
    key_findings: [],
    recommendations: [],
    exercise_controller: 'Michael Chen',
    evaluators: ['Supply Chain Expert', 'Operations Consultant'],
    created_by: 'Michael Chen',
    created_date: '2024-11-01',
    last_modified: '2024-11-15',
    tags: ['Supply Chain', 'Operations', 'Quarterly'],
    cost: 12000
  },
  {
    id: 'exercise-003',
    name: 'Pandemic Response Walkthrough',
    description: 'Review and validate pandemic response procedures and remote work capabilities',
    type: 'walkthrough',
    status: 'planning',
    scheduled_date: '2024-11-25',
    start_time: '10:00',
    end_time: '14:00',
    duration_minutes: 240,
    location: 'Virtual/Teams',
    facilitator: 'Lisa Wang',
    objectives: [
      {
        id: 'obj-006',
        description: 'Validate remote work procedures',
        success_criteria: 'All critical functions can operate remotely',
        priority: 'high'
      }
    ],
    scenario: {
      id: 'scenario-003',
      title: 'Novel Virus Outbreak',
      description: 'Rapid spread of new virus requiring immediate transition to remote work',
      threat_type: 'pandemic',
      severity_level: 'medium',
      affected_systems: ['Office Facilities', 'On-site Operations', 'Customer Service'],
      timeline: [
        {
          time: '10:00',
          event: 'Government announces lockdown measures',
          inject_type: 'initial'
        },
        {
          time: '11:30',
          event: 'Multiple employee exposures reported',
          inject_type: 'escalation'
        }
      ],
      expected_responses: [
        'Activate remote work protocols',
        'Ensure system access for all staff',
        'Maintain customer service levels',
        'Monitor employee health and welfare'
      ],
      evaluation_criteria: [
        'Speed of remote work transition',
        'Maintenance of service levels',
        'Employee communication effectiveness'
      ]
    },
    participants: [
      {
        id: 'participant-006',
        name: 'HR Director',
        role: 'HR Director',
        department: 'Human Resources',
        email: 'hr.director@company.com',
        participation_type: 'player',
        attendance_status: 'confirmed'
      }
    ],
    scope: ['Remote Work', 'Employee Health', 'Customer Service'],
    focus_areas: ['Technology Infrastructure', 'Employee Support', 'Service Continuity'],
    systems_tested: ['VPN', 'Video Conferencing', 'Remote Access'],
    plans_tested: ['Pandemic Response Plan', 'Remote Work Plan'],
    observations: [],
    lessons_learned: [],
    action_items: [],
    overall_rating: 'satisfactory',
    success_percentage: 0,
    key_findings: [],
    recommendations: [],
    exercise_controller: 'Lisa Wang',
    evaluators: ['HR Consultant', 'IT Security Expert'],
    created_by: 'Lisa Wang',
    created_date: '2024-11-05',
    last_modified: '2024-11-10',
    tags: ['Pandemic', 'Remote Work', 'Health'],
    cost: 5000
  }
]

const generateMockProgram = (): ExerciseProgram => ({
  id: 'program-2024',
  name: 'Annual BCM Exercise Program 2024',
  description: 'Comprehensive exercise program to test and validate business continuity capabilities',
  year: 2024,
  objectives: [
    'Test all critical business continuity plans',
    'Validate incident response procedures',
    'Assess organizational preparedness',
    'Identify improvement opportunities',
    'Build muscle memory for crisis response'
  ],
  schedule: [
    {
      quarter: 1,
      exercises: [],
      milestones: [
        {
          date: '2024-03-31',
          title: 'Q1 Exercise Planning Complete',
          description: 'All Q2 exercises planned and scheduled'
        }
      ]
    },
    {
      quarter: 2,
      exercises: [],
      milestones: [
        {
          date: '2024-06-30',
          title: 'Mid-year Review',
          description: 'Review exercise outcomes and adjust program'
        }
      ]
    },
    {
      quarter: 3,
      exercises: [
        {
          id: 'exercise-001',
          name: 'Cyber Incident Response Exercise 2024',
          description: 'Comprehensive tabletop exercise testing cyber incident response procedures',
          type: 'tabletop',
          status: 'completed',
          scheduled_date: '2024-10-15',
          start_time: '09:00',
          end_time: '16:00',
          duration_minutes: 420,
          location: 'Executive Conference Room',
          facilitator: 'Sarah Johnson',
          objectives: [],
          scenario: {} as ExerciseScenario,
          participants: [],
          scope: [],
          focus_areas: [],
          systems_tested: [],
          plans_tested: [],
          observations: [],
          lessons_learned: [],
          action_items: [],
          overall_rating: 'good',
          success_percentage: 82,
          key_findings: [],
          recommendations: [],
          exercise_controller: 'Sarah Johnson',
          evaluators: [],
          created_by: 'Sarah Johnson',
          created_date: '2024-09-01',
          last_modified: '2024-10-20',
          tags: [],
          cost: 15000
        }
      ],
      milestones: [
        {
          date: '2024-09-30',
          title: 'Annual Cyber Exercise',
          description: 'Major cybersecurity incident response exercise'
        }
      ]
    },
    {
      quarter: 4,
      exercises: [
        {
          id: 'exercise-002',
          name: 'Supply Chain Disruption Exercise',
          description: 'Functional exercise simulating major supply chain disruption and response',
          type: 'functional',
          status: 'scheduled',
          scheduled_date: '2024-12-10',
          start_time: '08:00',
          end_time: '17:00',
          duration_minutes: 540,
          location: 'Operations Center',
          facilitator: 'Michael Chen',
          objectives: [],
          scenario: {} as ExerciseScenario,
          participants: [],
          scope: [],
          focus_areas: [],
          systems_tested: [],
          plans_tested: [],
          observations: [],
          lessons_learned: [],
          action_items: [],
          overall_rating: 'satisfactory',
          success_percentage: 0,
          key_findings: [],
          recommendations: [],
          exercise_controller: 'Michael Chen',
          evaluators: [],
          created_by: 'Michael Chen',
          created_date: '2024-11-01',
          last_modified: '2024-11-15',
          tags: [],
          cost: 12000
        }
      ],
      milestones: [
        {
          date: '2024-12-31',
          title: 'Annual Program Review',
          description: 'Complete evaluation of exercise program effectiveness'
        }
      ]
    }
  ],
  budget: 50000,
  resource_requirements: [
    'External facilitators and evaluators',
    'Venue rentals and logistics',
    'Technology and simulation tools',
    'Participant time and travel',
    'Documentation and reporting'
  ],
  success_metrics: [
    'All planned exercises completed',
    'Average exercise rating > 3.5/5',
    'Action item completion rate > 90%',
    'Participant satisfaction > 80%',
    'Measurable improvement in preparedness'
  ],
  status: 'active'
})

export function ExerciseModule() {
  const [activeTab, setActiveTab] = useState('overview')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterType, setFilterType] = useState<string>('all')
  const [selectedDate, setSelectedDate] = useState<Date>()

  // Store integration
  const { currentModule, setCurrentModule } = useBCMStore()

  // Data fetching
  const { data: exercises = [], isLoading: loadingExercises } = useQuery({
    queryKey: ['exercises'],
    queryFn: async () => {
      // API client doesn't have exercises endpoint, using mock data
      return generateMockExercises()
    }
  })

  const { data: exerciseProgram, isLoading: loadingProgram } = useQuery({
    queryKey: ['exercise-program'],
    queryFn: async () => {
      // API client doesn't have exercises endpoint
      return generateMockProgram()
    }
  })

  // Metrics calculations
  const totalExercises = exercises.length
  const completedExercises = exercises.filter(e => e.status === 'completed').length
  const scheduledExercises = exercises.filter(e => e.status === 'scheduled').length
  const planningExercises = exercises.filter(e => e.status === 'planning').length

  const totalActionItems = exercises.reduce((sum, exercise) => sum + exercise.action_items.length, 0)
  const completedActionItems = exercises.reduce((sum, exercise) =>
    sum + exercise.action_items.filter(item => item.status === 'completed').length, 0)

  const averageRating = exercises.filter(e => e.participant_feedback_summary).length > 0
    ? exercises.filter(e => e.participant_feedback_summary)
        .reduce((sum, e) => sum + e.participant_feedback_summary!.average_rating, 0) /
      exercises.filter(e => e.participant_feedback_summary).length
    : 0

  const averageSuccess = exercises.filter(e => e.success_percentage > 0).length > 0
    ? exercises.filter(e => e.success_percentage > 0)
        .reduce((sum, e) => sum + e.success_percentage, 0) /
      exercises.filter(e => e.success_percentage > 0).length
    : 0

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50'
      case 'in_progress': return 'text-blue-600 bg-blue-50'
      case 'scheduled': return 'text-orange-600 bg-orange-50'
      case 'planning': return 'text-yellow-600 bg-yellow-50'
      case 'cancelled': case 'postponed': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'tabletop': return 'text-blue-600 bg-blue-50'
      case 'functional': return 'text-green-600 bg-green-50'
      case 'full_scale': return 'text-red-600 bg-red-50'
      case 'walkthrough': return 'text-yellow-600 bg-yellow-50'
      case 'drill': return 'text-purple-600 bg-purple-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'excellent': return 'text-green-600 bg-green-50'
      case 'good': return 'text-blue-600 bg-blue-50'
      case 'satisfactory': return 'text-yellow-600 bg-yellow-50'
      case 'needs_improvement': return 'text-orange-600 bg-orange-50'
      case 'poor': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50'
      case 'high': return 'text-orange-600 bg-orange-50'
      case 'medium': return 'text-yellow-600 bg-yellow-50'
      case 'low': return 'text-green-600 bg-green-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Exercise Management</h1>
          <p className="text-gray-600 mt-1">Plan, conduct, and evaluate business continuity exercises and testing</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Program
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Create Exercise
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="exercises">Exercises</TabsTrigger>
          <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
          <TabsTrigger value="program">Program</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Exercises</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalExercises}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {completedExercises} completed, {scheduledExercises} scheduled
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{Math.round(averageSuccess)}%</div>
                <div className="text-xs text-muted-foreground mt-1">
                  Average exercise success
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Action Items</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalActionItems}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {completedActionItems} completed ({totalActionItems > 0 ? Math.round((completedActionItems / totalActionItems) * 100) : 0}%)
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Participant Rating</CardTitle>
                <Award className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{averageRating.toFixed(1)}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  Average participant satisfaction
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Upcoming Exercises */}
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Exercises</CardTitle>
              <CardDescription>Scheduled and planned exercises requiring attention</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {exercises
                  .filter(e => e.status === 'scheduled' || e.status === 'planning')
                  .sort((a, b) => new Date(a.scheduled_date).getTime() - new Date(b.scheduled_date).getTime())
                  .map((exercise) => (
                    <div key={exercise.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <Target className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="font-medium">{exercise.name}</h4>
                          <p className="text-sm text-gray-600">{exercise.description}</p>
                          <div className="flex items-center space-x-4 mt-2">
                            <Badge variant="outline" className={getStatusColor(exercise.status)}>
                              {exercise.status}
                            </Badge>
                            <Badge variant="outline" className={getTypeColor(exercise.type)}>
                              {exercise.type}
                            </Badge>
                            <span className="text-xs text-gray-500">
                              {exercise.participants.length} participants
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">
                          {format(new Date(exercise.scheduled_date), 'MMM dd, yyyy')}
                        </div>
                        <div className="text-xs text-gray-500">
                          {exercise.start_time} - {exercise.end_time}
                        </div>
                        <div className="text-xs text-gray-500">
                          Facilitator: {exercise.facilitator}
                        </div>
                      </div>
                    </div>
                  ))}
                {exercises.filter(e => e.status === 'scheduled' || e.status === 'planning').length === 0 && (
                  <div className="text-center py-6">
                    <Target className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">No upcoming exercises scheduled</p>
                    <Button variant="outline"  className="mt-2">
                      <Plus className="h-4 w-4 mr-2" />
                      Schedule Exercise
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Recent Exercise Results */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Recent Exercise Results</CardTitle>
                <CardDescription>Latest completed exercise outcomes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {exercises
                    .filter(e => e.status === 'completed')
                    .sort((a, b) => new Date(b.scheduled_date).getTime() - new Date(a.scheduled_date).getTime())
                    .slice(0, 3)
                    .map((exercise) => (
                      <div key={exercise.id} className="p-3 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-sm">{exercise.name}</h4>
                          <Badge variant="outline" className={getRatingColor(exercise.overall_rating)}>
                            {exercise.overall_rating}
                          </Badge>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span>Success Rate: {exercise.success_percentage}%</span>
                          <span>Actions: {exercise.action_items.length}</span>
                        </div>
                        <Progress value={exercise.success_percentage} className="mt-2" />
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Open Action Items</CardTitle>
                <CardDescription>Follow-up actions from recent exercises</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {exercises
                    .flatMap(e => e.action_items)
                    .filter(item => item.status !== 'completed')
                    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
                    .slice(0, 5)
                    .map((item) => (
                      <div key={item.id} className="flex items-center justify-between">
                        <div className="flex-1">
                          <h5 className="font-medium text-sm">{item.description}</h5>
                          <p className="text-xs text-gray-600">Responsible: {item.responsible}</p>
                        </div>
                        <div className="text-right">
                          <Badge variant="outline" className={
                            item.priority === 'high' ? 'text-red-600 bg-red-50' :
                            item.priority === 'medium' ? 'text-yellow-600 bg-yellow-50' :
                            'text-green-600 bg-green-50'
                          } >
                            {item.priority}
                          </Badge>
                          <div className="text-xs text-gray-500 mt-1">
                            Due: {format(new Date(item.due_date), 'MMM dd')}
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Exercises Tab */}
        <TabsContent value="exercises" className="space-y-6">
          {/* Exercise Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Exercise Library</CardTitle>
              <CardDescription>Comprehensive view of all planned, scheduled, and completed exercises</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search exercises..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="planning">Planning</SelectItem>
                    <SelectItem value="scheduled">Scheduled</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterType} onValueChange={setFilterType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="tabletop">Tabletop</SelectItem>
                    <SelectItem value="functional">Functional</SelectItem>
                    <SelectItem value="full_scale">Full Scale</SelectItem>
                    <SelectItem value="walkthrough">Walkthrough</SelectItem>
                    <SelectItem value="drill">Drill</SelectItem>
                  </SelectContent>
                </Select>
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Apply Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Exercises List */}
          <div className="grid gap-6">
            {exercises.map((exercise) => (
              <Card key={exercise.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{exercise.name}</CardTitle>
                      <CardDescription>{exercise.description}</CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className={getStatusColor(exercise.status)}>
                        {exercise.status}
                      </Badge>
                      <Badge variant="outline" className={getTypeColor(exercise.type)}>
                        {exercise.type}
                      </Badge>
                      {exercise.overall_rating && (
                        <Badge variant="outline" className={getRatingColor(exercise.overall_rating)}>
                          {exercise.overall_rating}
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <span className="text-sm font-medium">Date & Time:</span>
                        <p className="text-sm text-gray-600">
                          {format(new Date(exercise.scheduled_date), 'MMM dd, yyyy')}
                        </p>
                        <p className="text-sm text-gray-600">
                          {exercise.start_time} - {exercise.end_time}
                        </p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Location:</span>
                        <p className="text-sm text-gray-600">{exercise.location}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Facilitator:</span>
                        <p className="text-sm text-gray-600">{exercise.facilitator}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Participants:</span>
                        <p className="text-sm text-gray-600">{exercise.participants.length} people</p>
                      </div>
                    </div>

                    <div>
                      <span className="text-sm font-medium">Scenario:</span>
                      <p className="text-sm text-gray-600">{exercise.scenario.title}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge variant="outline" className={getSeverityColor(exercise.scenario.severity_level)} >
                          {exercise.scenario.severity_level}
                        </Badge>
                        <span className="text-xs text-gray-500">{exercise.scenario.threat_type.replace('_', ' ')}</span>
                      </div>
                    </div>

                    <div>
                      <span className="text-sm font-medium">Objectives:</span>
                      <div className="mt-1">
                        {exercise.objectives.slice(0, 2).map((objective) => (
                          <div key={objective.id} className="flex items-center space-x-2 text-sm">
                            <div className={cn(
                              'w-2 h-2 rounded-full',
                              objective.achieved === true ? 'bg-green-500' :
                              objective.achieved === false ? 'bg-red-500' :
                              'bg-gray-300'
                            )} />
                            <span className="text-gray-600">{objective.description}</span>
                          </div>
                        ))}
                        {exercise.objectives.length > 2 && (
                          <span className="text-xs text-gray-500">+{exercise.objectives.length - 2} more objectives</span>
                        )}
                      </div>
                    </div>

                    {exercise.status === 'completed' && (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
                        <div>
                          <span className="text-sm font-medium">Success Rate:</span>
                          <div className="flex items-center space-x-2 mt-1">
                            <Progress value={exercise.success_percentage} className="flex-1" />
                            <span className="text-sm font-medium">{exercise.success_percentage}%</span>
                          </div>
                        </div>
                        <div>
                          <span className="text-sm font-medium">Action Items:</span>
                          <p className="text-sm text-gray-600">
                            {exercise.action_items.length} total, {exercise.action_items.filter(a => a.status === 'completed').length} completed
                          </p>
                        </div>
                        <div>
                          <span className="text-sm font-medium">Participant Rating:</span>
                          <p className="text-sm text-gray-600">
                            {exercise.participant_feedback_summary?.average_rating || 'N/A'}/5.0
                          </p>
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" >
                          <Eye className="h-4 w-4 mr-2" />
                          View Details
                        </Button>
                        <Button variant="outline" >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </Button>
                        {exercise.status === 'completed' && (
                          <Button variant="outline" >
                            <Download className="h-4 w-4 mr-2" />
                            Report
                          </Button>
                        )}
                      </div>
                      <div className="text-xs text-gray-500">
                        Created: {format(new Date(exercise.created_date), 'MMM dd, yyyy')}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Scenarios Tab */}
        <TabsContent value="scenarios" className="space-y-6">
          {/* Scenario Library */}
          <Card>
            <CardHeader>
              <CardTitle>Exercise Scenarios</CardTitle>
              <CardDescription>Library of exercise scenarios and threat models</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6">
                {exercises.map((exercise) => (
                  <div key={exercise.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="font-medium">{exercise.scenario.title}</h4>
                        <p className="text-sm text-gray-600">{exercise.scenario.description}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className={getSeverityColor(exercise.scenario.severity_level)}>
                          {exercise.scenario.severity_level}
                        </Badge>
                        <Badge variant="outline">
                          {exercise.scenario.threat_type.replace('_', ' ')}
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <span className="text-sm font-medium">Affected Systems:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {exercise.scenario.affected_systems.map((system, index) => (
                            <Badge key={index} variant="outline" >
                              {system}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Expected Responses:</span>
                        <ul className="text-sm text-gray-600 mt-1 list-disc list-inside">
                          {exercise.scenario.expected_responses.slice(0, 3).map((response, index) => (
                            <li key={index}>{response}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <div className="mt-4">
                      <span className="text-sm font-medium">Timeline:</span>
                      <div className="mt-2 space-y-2">
                        {exercise.scenario.timeline.slice(0, 3).map((event, index) => (
                          <div key={index} className="flex items-center space-x-3 text-sm">
                            <span className="font-mono text-gray-500 w-12">{event.time}</span>
                            <div className={cn(
                              'w-2 h-2 rounded-full',
                              event.inject_type === 'initial' ? 'bg-blue-500' :
                              event.inject_type === 'escalation' ? 'bg-orange-500' :
                              event.inject_type === 'complication' ? 'bg-red-500' :
                              'bg-gray-400'
                            )} />
                            <span className="text-gray-600">{event.event}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t mt-4">
                      <div className="text-xs text-gray-500">
                        Used in: {exercise.name}
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" >
                          <Eye className="h-4 w-4 mr-2" />
                          View Full Scenario
                        </Button>
                        <Button variant="outline" >
                          <Copy className="h-4 w-4 mr-2" />
                          Duplicate
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Program Tab */}
        <TabsContent value="program" className="space-y-6">
          {/* Program Overview */}
          {exerciseProgram && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>{exerciseProgram.name}</CardTitle>
                  <CardDescription>{exerciseProgram.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <h4 className="font-medium mb-3">Program Objectives</h4>
                      <ul className="space-y-2">
                        {exerciseProgram.objectives.map((objective, index) => (
                          <li key={index} className="flex items-center space-x-2">
                            <Target className="h-4 w-4 text-blue-500" />
                            <span className="text-sm">{objective}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div>
                        <h4 className="font-medium mb-2">Budget & Resources</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>Total Budget:</span>
                            <span>${exerciseProgram.budget.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Spent:</span>
                            <span>${exercises.reduce((sum, e) => sum + e.cost, 0).toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Remaining:</span>
                            <span>${(exerciseProgram.budget - exercises.reduce((sum, e) => sum + e.cost, 0)).toLocaleString()}</span>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Resource Requirements</h4>
                        <ul className="space-y-1 text-sm">
                          {exerciseProgram.resource_requirements.slice(0, 3).map((resource, index) => (
                            <li key={index} className="text-gray-600">• {resource}</li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Success Metrics</h4>
                        <ul className="space-y-1 text-sm">
                          {exerciseProgram.success_metrics.slice(0, 3).map((metric, index) => (
                            <li key={index} className="flex items-center space-x-2">
                              <BarChart3 className="h-3 w-3 text-green-500" />
                              <span className="text-gray-600">{metric}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Quarterly Schedule */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {exerciseProgram.schedule.map((quarter) => (
                  <Card key={quarter.quarter}>
                    <CardHeader>
                      <CardTitle>Q{quarter.quarter} {exerciseProgram.year}</CardTitle>
                      <CardDescription>{quarter.exercises.length} exercises planned</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {quarter.exercises.length > 0 ? (
                          quarter.exercises.map((exercise) => (
                            <div key={exercise.id} className="p-3 border rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium text-sm">{exercise.name}</h4>
                                <Badge variant="outline" className={getStatusColor(exercise.status)}>
                                  {exercise.status}
                                </Badge>
                              </div>
                              <div className="text-xs text-gray-600 mb-2">
                                {format(new Date(exercise.scheduled_date), 'MMM dd, yyyy')} • {exercise.type}
                              </div>
                              <div className="text-xs text-gray-500">
                                Facilitator: {exercise.facilitator}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="text-center py-6">
                            <CalendarIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                            <p className="text-sm text-gray-500">No exercises planned</p>
                          </div>
                        )}

                        {quarter.milestones.length > 0 && (
                          <div className="pt-4 border-t">
                            <h5 className="font-medium text-sm mb-2">Milestones</h5>
                            {quarter.milestones.map((milestone, index) => (
                              <div key={index} className="text-xs text-gray-600">
                                <span className="font-medium">{format(new Date(milestone.date), 'MMM dd')}</span>: {milestone.title}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          {/* Exercise Analytics */}
          <Card>
            <CardHeader>
              <CardTitle>Exercise Program Analytics</CardTitle>
              <CardDescription>Performance metrics and trend analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{exercises.length}</div>
                  <div className="text-sm text-gray-600">Total Exercises</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{Math.round(averageSuccess)}%</div>
                  <div className="text-sm text-gray-600">Avg Success Rate</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">{averageRating.toFixed(1)}</div>
                  <div className="text-sm text-gray-600">Participant Rating</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {totalActionItems > 0 ? Math.round((completedActionItems / totalActionItems) * 100) : 0}%
                  </div>
                  <div className="text-sm text-gray-600">Action Completion</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Exercise Type Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Exercise Type Distribution</CardTitle>
              <CardDescription>Breakdown of exercises by type and complexity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {['tabletop', 'functional', 'full_scale', 'walkthrough', 'drill'].map((type) => {
                  const count = exercises.filter(e => e.type === type).length
                  const percentage = exercises.length > 0 ? (count / exercises.length) * 100 : 0
                  const avgSuccess = exercises.filter(e => e.type === type && e.success_percentage > 0).length > 0
                    ? exercises.filter(e => e.type === type && e.success_percentage > 0)
                        .reduce((sum, e) => sum + e.success_percentage, 0) /
                      exercises.filter(e => e.type === type && e.success_percentage > 0).length
                    : 0

                  return (
                    <div key={type} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <h4 className="font-medium capitalize">{type.replace('_', ' ')}</h4>
                        <p className="text-sm text-gray-600">{count} exercises • {Math.round(avgSuccess)}% avg success</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Progress value={percentage} className="w-24" />
                        <span className="text-sm font-medium">{percentage.toFixed(1)}%</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Lessons Learned Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Common Lessons Learned</CardTitle>
              <CardDescription>Recurring themes and improvement areas</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {exercises
                  .filter(e => e.lessons_learned.length > 0)
                  .flatMap(e => e.lessons_learned)
                  .slice(0, 8)
                  .map((lesson, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <Lightbulb className="h-4 w-4 text-yellow-500 mt-0.5" />
                      <span className="text-sm text-gray-600">{lesson}</span>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}