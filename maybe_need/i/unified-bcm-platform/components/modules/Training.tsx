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
  BookOpen,
  Users,
  Target,
  Award,
  Calendar as CalendarIcon,
  Clock,
  Play,
  Pause,
  CheckCircle,
  XCircle,
  AlertCircle,
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  Edit,
  Eye,
  BarChart3,
  TrendingUp,
  Video,
  FileText,
  Headphones,
  Monitor,
  User,
  Star
} from 'lucide-react'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'

// Types
interface TrainingCourse {
  id: string
  title: string
  description: string
  category: 'bcm_fundamentals' | 'crisis_management' | 'risk_assessment' | 'plan_development' | 'exercise_management' | 'leadership' | 'communication'
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  format: 'online' | 'classroom' | 'blended' | 'workshop' | 'simulation'
  duration: number // minutes
  modules: TrainingModule[]
  prerequisites: string[]
  learningObjectives: string[]
  assessmentCriteria: string[]
  certificationType: 'completion' | 'assessment' | 'accredited' | 'none'
  validityPeriod?: number // months
  instructor?: string
  tags: string[]
  status: 'draft' | 'active' | 'archived'
  createdDate: string
  updatedDate: string
}

interface TrainingModule {
  id: string
  title: string
  description: string
  type: 'video' | 'document' | 'quiz' | 'practical' | 'discussion'
  duration: number // minutes
  content: string
  resources: string[]
  order: number
  required: boolean
}

interface TrainingEnrollment {
  id: string
  userId: string
  userName: string
  userDepartment: string
  courseId: string
  courseName: string
  enrollmentDate: string
  startDate?: string
  completionDate?: string
  status: 'enrolled' | 'in_progress' | 'completed' | 'failed' | 'expired'
  progress: number // percentage
  currentModule?: string
  timeSpent: number // minutes
  attempts: number
  score?: number
  certificateId?: string
  notes?: string
}

interface TrainingRecord {
  id: string
  userId: string
  userName: string
  department: string
  position: string
  completedCourses: TrainingEnrollment[]
  mandatoryCompliance: {
    required: string[]
    completed: string[]
    overdue: string[]
    upcoming: string[]
  }
  certifications: {
    id: string
    name: string
    issueDate: string
    expiryDate: string
    status: 'active' | 'expired' | 'pending'
  }[]
  competencyLevel: 'basic' | 'competent' | 'proficient' | 'expert'
  lastTrainingDate?: string
  nextRequiredTraining?: string
}

interface TrainingPlan {
  id: string
  name: string
  description: string
  targetAudience: string[]
  objectives: string[]
  schedule: {
    startDate: string
    endDate: string
    milestones: {
      date: string
      title: string
      description: string
    }[]
  }
  courses: {
    courseId: string
    courseName: string
    mandatory: boolean
    deadline?: string
    targetGroups: string[]
  }[]
  budget: number
  resources: string[]
  successMetrics: string[]
  status: 'planning' | 'active' | 'completed' | 'on_hold'
}

// Mock Data
const generateMockCourses = (): TrainingCourse[] => [
  {
    id: 'course-001',
    title: 'BCM Fundamentals',
    description: 'Introduction to Business Continuity Management principles and ISO 22301 requirements',
    category: 'bcm_fundamentals',
    level: 'beginner',
    format: 'online',
    duration: 120,
    modules: [
      {
        id: 'module-001',
        title: 'Introduction to BCM',
        description: 'Overview of business continuity concepts',
        type: 'video',
        duration: 30,
        content: 'BCM_Intro_Video.mp4',
        resources: ['BCM_Handbook.pdf', 'ISO22301_Overview.pdf'],
        order: 1,
        required: true
      },
      {
        id: 'module-002',
        title: 'Business Impact Analysis',
        description: 'Understanding BIA methodology',
        type: 'document',
        duration: 45,
        content: 'BIA_Guide.pdf',
        resources: ['BIA_Template.xlsx', 'BIA_Examples.pdf'],
        order: 2,
        required: true
      },
      {
        id: 'module-003',
        title: 'Knowledge Check',
        description: 'Assessment of BCM fundamentals',
        type: 'quiz',
        duration: 15,
        content: 'fundamentals_quiz',
        resources: [],
        order: 3,
        required: true
      }
    ],
    prerequisites: [],
    learningObjectives: [
      'Understand BCM principles and terminology',
      'Identify key BCM processes',
      'Recognize the importance of business continuity planning'
    ],
    assessmentCriteria: [
      'Pass quiz with 80% or higher',
      'Complete all required modules'
    ],
    certificationType: 'completion',
    validityPeriod: 12,
    instructor: 'Sarah Johnson, BCM Expert',
    tags: ['BCM', 'ISO 22301', 'Fundamentals'],
    status: 'active',
    createdDate: '2024-01-15',
    updatedDate: '2024-10-01'
  },
  {
    id: 'course-002',
    title: 'Crisis Management Leadership',
    description: 'Advanced course for crisis team leaders and decision makers',
    category: 'crisis_management',
    level: 'advanced',
    format: 'blended',
    duration: 480,
    modules: [
      {
        id: 'module-004',
        title: 'Crisis Leadership Principles',
        description: 'Leadership during crisis situations',
        type: 'video',
        duration: 60,
        content: 'Crisis_Leadership.mp4',
        resources: ['Leadership_Guide.pdf'],
        order: 1,
        required: true
      },
      {
        id: 'module-005',
        title: 'Decision Making Under Pressure',
        description: 'Structured decision making processes',
        type: 'practical',
        duration: 90,
        content: 'decision_making_exercise',
        resources: ['Decision_Framework.pdf'],
        order: 2,
        required: true
      },
      {
        id: 'module-006',
        title: 'Crisis Communication',
        description: 'Effective communication strategies',
        type: 'workshop',
        duration: 120,
        content: 'communication_workshop',
        resources: ['Communication_Templates.docx'],
        order: 3,
        required: true
      }
    ],
    prerequisites: ['BCM Fundamentals', '2 years BCM experience'],
    learningObjectives: [
      'Develop crisis leadership skills',
      'Master decision-making frameworks',
      'Implement effective communication strategies'
    ],
    assessmentCriteria: [
      'Practical exercise evaluation',
      'Leadership scenario assessment',
      'Communication skills demonstration'
    ],
    certificationType: 'accredited',
    validityPeriod: 24,
    instructor: 'Michael Chen, Crisis Management Consultant',
    tags: ['Crisis Management', 'Leadership', 'Advanced'],
    status: 'active',
    createdDate: '2024-02-01',
    updatedDate: '2024-09-15'
  },
  {
    id: 'course-003',
    title: 'Exercise Planning & Management',
    description: 'Planning and conducting business continuity exercises',
    category: 'exercise_management',
    level: 'intermediate',
    format: 'workshop',
    duration: 360,
    modules: [
      {
        id: 'module-007',
        title: 'Exercise Types and Objectives',
        description: 'Different types of BCM exercises',
        type: 'document',
        duration: 45,
        content: 'Exercise_Types.pdf',
        resources: ['Exercise_Planning_Guide.pdf'],
        order: 1,
        required: true
      },
      {
        id: 'module-008',
        title: 'Scenario Development',
        description: 'Creating realistic exercise scenarios',
        type: 'practical',
        duration: 90,
        content: 'scenario_development',
        resources: ['Scenario_Templates.docx'],
        order: 2,
        required: true
      }
    ],
    prerequisites: ['BCM Fundamentals'],
    learningObjectives: [
      'Plan effective BCM exercises',
      'Develop realistic scenarios',
      'Conduct exercise evaluation'
    ],
    assessmentCriteria: [
      'Exercise plan development',
      'Scenario creation exercise'
    ],
    certificationType: 'assessment',
    validityPeriod: 18,
    instructor: 'Lisa Wang, Exercise Specialist',
    tags: ['Exercises', 'Planning', 'Testing'],
    status: 'active',
    createdDate: '2024-03-10',
    updatedDate: '2024-08-20'
  }
]

const generateMockEnrollments = (): TrainingEnrollment[] => [
  {
    id: 'enrollment-001',
    userId: 'user-001',
    userName: 'John Smith',
    userDepartment: 'IT',
    courseId: 'course-001',
    courseName: 'BCM Fundamentals',
    enrollmentDate: '2024-10-01',
    startDate: '2024-10-02',
    completionDate: '2024-10-15',
    status: 'completed',
    progress: 100,
    timeSpent: 125,
    attempts: 1,
    score: 92,
    certificateId: 'cert-001',
    notes: 'Excellent performance'
  },
  {
    id: 'enrollment-002',
    userId: 'user-002',
    userName: 'Sarah Johnson',
    userDepartment: 'Operations',
    courseId: 'course-002',
    courseName: 'Crisis Management Leadership',
    enrollmentDate: '2024-09-15',
    startDate: '2024-09-20',
    status: 'in_progress',
    progress: 65,
    currentModule: 'module-006',
    timeSpent: 280,
    attempts: 1,
    notes: 'Strong leadership potential'
  },
  {
    id: 'enrollment-003',
    userId: 'user-003',
    userName: 'Mike Chen',
    userDepartment: 'Finance',
    courseId: 'course-001',
    courseName: 'BCM Fundamentals',
    enrollmentDate: '2024-11-01',
    status: 'enrolled',
    progress: 0,
    timeSpent: 0,
    attempts: 0
  },
  {
    id: 'enrollment-004',
    userId: 'user-004',
    userName: 'Lisa Wang',
    userDepartment: 'HR',
    courseId: 'course-003',
    courseName: 'Exercise Planning & Management',
    enrollmentDate: '2024-10-10',
    startDate: '2024-10-12',
    status: 'in_progress',
    progress: 45,
    currentModule: 'module-008',
    timeSpent: 160,
    attempts: 1
  },
  {
    id: 'enrollment-005',
    userId: 'user-005',
    userName: 'David Brown',
    userDepartment: 'Security',
    courseId: 'course-001',
    courseName: 'BCM Fundamentals',
    enrollmentDate: '2024-09-01',
    startDate: '2024-09-05',
    status: 'failed',
    progress: 85,
    timeSpent: 110,
    attempts: 2,
    score: 65,
    notes: 'Requires additional support'
  }
]

const generateMockTrainingRecords = (): TrainingRecord[] => [
  {
    id: 'record-001',
    userId: 'user-001',
    userName: 'John Smith',
    department: 'IT',
    position: 'IT Manager',
    completedCourses: [
      {
        id: 'enrollment-001',
        userId: 'user-001',
        userName: 'John Smith',
        userDepartment: 'IT',
        courseId: 'course-001',
        courseName: 'BCM Fundamentals',
        enrollmentDate: '2024-10-01',
        completionDate: '2024-10-15',
        status: 'completed',
        progress: 100,
        timeSpent: 125,
        attempts: 1,
        score: 92
      }
    ],
    mandatoryCompliance: {
      required: ['BCM Fundamentals', 'Crisis Management Leadership'],
      completed: ['BCM Fundamentals'],
      overdue: [],
      upcoming: ['Crisis Management Leadership']
    },
    certifications: [
      {
        id: 'cert-001',
        name: 'BCM Fundamentals Certificate',
        issueDate: '2024-10-15',
        expiryDate: '2025-10-15',
        status: 'active'
      }
    ],
    competencyLevel: 'competent',
    lastTrainingDate: '2024-10-15',
    nextRequiredTraining: '2024-12-01'
  },
  {
    id: 'record-002',
    userId: 'user-002',
    userName: 'Sarah Johnson',
    department: 'Operations',
    position: 'Operations Director',
    completedCourses: [],
    mandatoryCompliance: {
      required: ['BCM Fundamentals', 'Crisis Management Leadership', 'Exercise Planning & Management'],
      completed: [],
      overdue: ['BCM Fundamentals'],
      upcoming: ['Crisis Management Leadership']
    },
    certifications: [],
    competencyLevel: 'basic',
    nextRequiredTraining: '2024-11-30'
  }
]

const generateMockTrainingPlan = (): TrainingPlan => ({
  id: 'plan-2024',
  name: 'Annual BCM Training Program 2024',
  description: 'Comprehensive training program to enhance organizational BCM capabilities',
  targetAudience: ['All Employees', 'Management Team', 'Crisis Response Team'],
  objectives: [
    'Achieve 95% completion rate for mandatory BCM training',
    'Develop crisis leadership capabilities',
    'Improve exercise planning and execution skills',
    'Enhance overall BCM competency across organization'
  ],
  schedule: {
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    milestones: [
      {
        date: '2024-03-31',
        title: 'Q1 Completion Target',
        description: 'Complete BCM Fundamentals for all new hires'
      },
      {
        date: '2024-06-30',
        title: 'Leadership Training',
        description: 'Complete Crisis Management Leadership for management team'
      },
      {
        date: '2024-09-30',
        title: 'Exercise Training',
        description: 'Complete Exercise Planning for response team members'
      },
      {
        date: '2024-12-31',
        title: 'Annual Review',
        description: 'Evaluate training effectiveness and plan for next year'
      }
    ]
  },
  courses: [
    {
      courseId: 'course-001',
      courseName: 'BCM Fundamentals',
      mandatory: true,
      deadline: '2024-12-31',
      targetGroups: ['All Employees']
    },
    {
      courseId: 'course-002',
      courseName: 'Crisis Management Leadership',
      mandatory: true,
      deadline: '2024-06-30',
      targetGroups: ['Management Team', 'Crisis Response Team']
    },
    {
      courseId: 'course-003',
      courseName: 'Exercise Planning & Management',
      mandatory: false,
      targetGroups: ['Crisis Response Team', 'BCM Team']
    }
  ],
  budget: 50000,
  resources: ['Learning Management System', 'External Trainers', 'Training Materials'],
  successMetrics: [
    'Completion rate > 95%',
    'Average score > 85%',
    'Participant satisfaction > 4.0/5.0',
    'Competency improvement measured'
  ],
  status: 'active'
})

export function TrainingModule() {
  const [activeTab, setActiveTab] = useState('overview')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterLevel, setFilterLevel] = useState<string>('all')
  const [selectedDate, setSelectedDate] = useState<Date>()

  // Store integration
  const { currentModule, setCurrentModule } = useBCMStore()

  // Data fetching
  const { data: courses = [], isLoading: loadingCourses } = useQuery({
    queryKey: ['training-courses'],
    queryFn: async () => {
      if (process.env.NEXT_PUBLIC_USE_REAL_API === 'true') {
        return await apiClient.training.getCourses()
      }
      return generateMockCourses()
    }
  })

  const { data: enrollments = [], isLoading: loadingEnrollments } = useQuery({
    queryKey: ['training-enrollments'],
    queryFn: async () => {
      if (process.env.NEXT_PUBLIC_USE_REAL_API === 'true') {
        return await apiClient.training.getEnrollments()
      }
      return generateMockEnrollments()
    }
  })

  const { data: trainingRecords = [], isLoading: loadingRecords } = useQuery({
    queryKey: ['training-records'],
    queryFn: async () => {
      if (process.env.NEXT_PUBLIC_USE_REAL_API === 'true') {
        return await apiClient.training.getRecords()
      }
      return generateMockTrainingRecords()
    }
  })

  const { data: trainingPlan, isLoading: loadingPlan } = useQuery({
    queryKey: ['training-plan'],
    queryFn: async () => {
      if (process.env.NEXT_PUBLIC_USE_REAL_API === 'true') {
        return await apiClient.training.getPlan()
      }
      return generateMockTrainingPlan()
    }
  })

  // Metrics calculations
  const totalCourses = courses.length
  const activeCourses = courses.filter(c => c.status === 'active').length

  const totalEnrollments = enrollments.length
  const completedEnrollments = enrollments.filter(e => e.status === 'completed').length
  const inProgressEnrollments = enrollments.filter(e => e.status === 'in_progress').length
  const failedEnrollments = enrollments.filter(e => e.status === 'failed').length

  const averageProgress = enrollments.length > 0
    ? Math.round(enrollments.reduce((sum, e) => sum + e.progress, 0) / enrollments.length)
    : 0

  const averageScore = enrollments.filter(e => e.score).length > 0
    ? Math.round(enrollments.filter(e => e.score).reduce((sum, e) => sum + (e.score || 0), 0) / enrollments.filter(e => e.score).length)
    : 0

  const overallCompletionRate = totalEnrollments > 0
    ? Math.round((completedEnrollments / totalEnrollments) * 100)
    : 0

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'beginner': return 'text-green-600 bg-green-50'
      case 'intermediate': return 'text-blue-600 bg-blue-50'
      case 'advanced': return 'text-orange-600 bg-orange-50'
      case 'expert': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50'
      case 'in_progress': return 'text-blue-600 bg-blue-50'
      case 'enrolled': return 'text-orange-600 bg-orange-50'
      case 'failed': return 'text-red-600 bg-red-50'
      case 'expired': return 'text-gray-600 bg-gray-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'online': return <Monitor className="h-4 w-4" />
      case 'classroom': return <Users className="h-4 w-4" />
      case 'blended': return <BookOpen className="h-4 w-4" />
      case 'workshop': return <Target className="h-4 w-4" />
      case 'simulation': return <Play className="h-4 w-4" />
      default: return <FileText className="h-4 w-4" />
    }
  }

  const getModuleTypeIcon = (type: string) => {
    switch (type) {
      case 'video': return <Video className="h-4 w-4" />
      case 'document': return <FileText className="h-4 w-4" />
      case 'quiz': return <CheckCircle className="h-4 w-4" />
      case 'practical': return <Target className="h-4 w-4" />
      case 'discussion': return <Users className="h-4 w-4" />
      default: return <BookOpen className="h-4 w-4" />
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Training Management</h1>
          <p className="text-gray-600 mt-1">Manage BCM training programs, courses, and learner progress</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Reports
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Create Course
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="courses">Courses</TabsTrigger>
          <TabsTrigger value="learners">Learners</TabsTrigger>
          <TabsTrigger value="records">Records</TabsTrigger>
          <TabsTrigger value="planning">Planning</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Courses</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalCourses}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {activeCourses} active courses
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{overallCompletionRate}%</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {completedEnrollments} of {totalEnrollments} enrollments
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Progress</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{averageProgress}%</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {inProgressEnrollments} in progress
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Score</CardTitle>
                <Star className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{averageScore}%</div>
                <div className="text-xs text-muted-foreground mt-1">
                  Learner performance
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Training Progress Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Enrollment Status</CardTitle>
                <CardDescription>Current learner enrollment distribution</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Completed</span>
                    <div className="flex items-center space-x-2">
                      <Progress value={(completedEnrollments / totalEnrollments) * 100} className="w-20" />
                      <span className="text-sm font-medium">{completedEnrollments}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">In Progress</span>
                    <div className="flex items-center space-x-2">
                      <Progress value={(inProgressEnrollments / totalEnrollments) * 100} className="w-20" />
                      <span className="text-sm font-medium">{inProgressEnrollments}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Failed</span>
                    <div className="flex items-center space-x-2">
                      <Progress value={(failedEnrollments / totalEnrollments) * 100} className="w-20" />
                      <span className="text-sm font-medium">{failedEnrollments}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Course Categories</CardTitle>
                <CardDescription>Distribution of courses by category</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {['bcm_fundamentals', 'crisis_management', 'exercise_management'].map((category) => {
                    const courseCount = courses.filter(c => c.category === category).length
                    return (
                      <div key={category} className="flex items-center justify-between">
                        <span className="text-sm capitalize">{category.replace('_', ' ')}</span>
                        <div className="flex items-center space-x-2">
                          <Progress value={(courseCount / totalCourses) * 100} className="w-20" />
                          <span className="text-sm font-medium">{courseCount}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Training Activity</CardTitle>
              <CardDescription>Latest enrollments and completions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {enrollments.slice(0, 5).map((enrollment) => (
                  <div key={enrollment.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium">{enrollment.userName}</h4>
                      <p className="text-sm text-gray-600">{enrollment.courseName}</p>
                      <div className="flex items-center space-x-4 mt-2">
                        <span className="text-xs text-gray-500">{enrollment.userDepartment}</span>
                        <Badge variant="outline" className={getStatusColor(enrollment.status)}>
                          {enrollment.status.replace('_', ' ')}
                        </Badge>
                        {enrollment.progress > 0 && (
                          <span className="text-xs text-gray-500">{enrollment.progress}% complete</span>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {enrollment.completionDate
                          ? format(new Date(enrollment.completionDate), 'MMM dd, yyyy')
                          : enrollment.startDate
                            ? format(new Date(enrollment.startDate), 'MMM dd, yyyy')
                            : format(new Date(enrollment.enrollmentDate), 'MMM dd, yyyy')
                        }
                      </div>
                      {enrollment.score && (
                        <div className="text-xs text-gray-500">Score: {enrollment.score}%</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Courses Tab */}
        <TabsContent value="courses" className="space-y-6">
          {/* Course Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Course Library</CardTitle>
              <CardDescription>Browse and manage training courses</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search courses..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={filterCategory} onValueChange={setFilterCategory}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    <SelectItem value="bcm_fundamentals">BCM Fundamentals</SelectItem>
                    <SelectItem value="crisis_management">Crisis Management</SelectItem>
                    <SelectItem value="risk_assessment">Risk Assessment</SelectItem>
                    <SelectItem value="exercise_management">Exercise Management</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterLevel} onValueChange={setFilterLevel}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Levels</SelectItem>
                    <SelectItem value="beginner">Beginner</SelectItem>
                    <SelectItem value="intermediate">Intermediate</SelectItem>
                    <SelectItem value="advanced">Advanced</SelectItem>
                    <SelectItem value="expert">Expert</SelectItem>
                  </SelectContent>
                </Select>
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Apply Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Courses Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <Card key={course.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getFormatIcon(course.format)}
                      <Badge variant="outline" className={getLevelColor(course.level)}>
                        {course.level}
                      </Badge>
                    </div>
                    <Badge variant={course.status === 'active' ? 'default' : 'secondary'}>
                      {course.status}
                    </Badge>
                  </div>
                  <CardTitle className="text-lg">{course.title}</CardTitle>
                  <CardDescription>{course.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Duration:</span>
                        <p className="text-gray-600">{Math.floor(course.duration / 60)}h {course.duration % 60}m</p>
                      </div>
                      <div>
                        <span className="font-medium">Format:</span>
                        <p className="text-gray-600 capitalize">{course.format}</p>
                      </div>
                      <div>
                        <span className="font-medium">Modules:</span>
                        <p className="text-gray-600">{course.modules.length} modules</p>
                      </div>
                      <div>
                        <span className="font-medium">Certificate:</span>
                        <p className="text-gray-600 capitalize">{course.certificationType}</p>
                      </div>
                    </div>

                    {course.tags.length > 0 && (
                      <div>
                        <span className="font-medium text-sm">Tags:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {course.tags.map((tag, index) => (
                            <Badge key={index} variant="outline" size="sm">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {course.instructor && (
                      <div>
                        <span className="font-medium text-sm">Instructor:</span>
                        <p className="text-sm text-gray-600">{course.instructor}</p>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-2" />
                          Preview
                        </Button>
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </Button>
                      </div>
                      <Button size="sm">
                        <Users className="h-4 w-4 mr-2" />
                        Enroll
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Learners Tab */}
        <TabsContent value="learners" className="space-y-6">
          {/* Learner Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Learner Management</CardTitle>
              <CardDescription>Track learner progress and performance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Input placeholder="Search learners..." />
                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="enrolled">Enrolled</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="failed">Failed</SelectItem>
                  </SelectContent>
                </Select>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by department" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Departments</SelectItem>
                    <SelectItem value="it">IT</SelectItem>
                    <SelectItem value="operations">Operations</SelectItem>
                    <SelectItem value="finance">Finance</SelectItem>
                    <SelectItem value="hr">HR</SelectItem>
                  </SelectContent>
                </Select>
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Apply Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Learners List */}
          <div className="grid gap-6">
            {enrollments.map((enrollment) => (
              <Card key={enrollment.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{enrollment.userName}</CardTitle>
                      <CardDescription>{enrollment.userDepartment} - {enrollment.courseName}</CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className={getStatusColor(enrollment.status)}>
                        {enrollment.status.replace('_', ' ')}
                      </Badge>
                      {enrollment.score && (
                        <Badge variant="outline">
                          Score: {enrollment.score}%
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <span className="text-sm font-medium">Enrolled:</span>
                        <p className="text-sm text-gray-600">{format(new Date(enrollment.enrollmentDate), 'MMM dd, yyyy')}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Progress:</span>
                        <div className="flex items-center space-x-2 mt-1">
                          <Progress value={enrollment.progress} className="flex-1" />
                          <span className="text-sm font-medium">{enrollment.progress}%</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Time Spent:</span>
                        <p className="text-sm text-gray-600">{Math.floor(enrollment.timeSpent / 60)}h {enrollment.timeSpent % 60}m</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Attempts:</span>
                        <p className="text-sm text-gray-600">{enrollment.attempts}</p>
                      </div>
                    </div>

                    {enrollment.currentModule && (
                      <div>
                        <span className="text-sm font-medium">Current Module:</span>
                        <p className="text-sm text-gray-600">{enrollment.currentModule}</p>
                      </div>
                    )}

                    {enrollment.completionDate && (
                      <div>
                        <span className="text-sm font-medium">Completed:</span>
                        <p className="text-sm text-gray-600">{format(new Date(enrollment.completionDate), 'MMM dd, yyyy')}</p>
                      </div>
                    )}

                    {enrollment.notes && (
                      <div>
                        <span className="text-sm font-medium">Notes:</span>
                        <p className="text-sm text-gray-600">{enrollment.notes}</p>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-2" />
                          View Details
                        </Button>
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4 mr-2" />
                          Update Progress
                        </Button>
                      </div>
                      {enrollment.certificateId && (
                        <Button variant="outline" size="sm">
                          <Award className="h-4 w-4 mr-2" />
                          View Certificate
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Records Tab */}
        <TabsContent value="records" className="space-y-6">
          {/* Training Records */}
          <Card>
            <CardHeader>
              <CardTitle>Training Records</CardTitle>
              <CardDescription>Comprehensive learner training history and compliance status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {trainingRecords.map((record) => (
                  <div key={record.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h4 className="font-medium">{record.userName}</h4>
                        <p className="text-sm text-gray-600">{record.position} - {record.department}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className={
                          record.competencyLevel === 'expert' ? 'text-purple-600 bg-purple-50' :
                          record.competencyLevel === 'proficient' ? 'text-blue-600 bg-blue-50' :
                          record.competencyLevel === 'competent' ? 'text-green-600 bg-green-50' :
                          'text-yellow-600 bg-yellow-50'
                        }>
                          {record.competencyLevel}
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h5 className="font-medium mb-2">Compliance Status</h5>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>Required Courses:</span>
                            <span>{record.mandatoryCompliance.required.length}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-green-600">Completed:</span>
                            <span>{record.mandatoryCompliance.completed.length}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-red-600">Overdue:</span>
                            <span>{record.mandatoryCompliance.overdue.length}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-orange-600">Upcoming:</span>
                            <span>{record.mandatoryCompliance.upcoming.length}</span>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h5 className="font-medium mb-2">Certifications</h5>
                        {record.certifications.length > 0 ? (
                          <div className="space-y-2">
                            {record.certifications.map((cert) => (
                              <div key={cert.id} className="flex items-center justify-between text-sm">
                                <span>{cert.name}</span>
                                <Badge variant="outline" className={
                                  cert.status === 'active' ? 'text-green-600 bg-green-50' :
                                  cert.status === 'expired' ? 'text-red-600 bg-red-50' :
                                  'text-yellow-600 bg-yellow-50'
                                }>
                                  {cert.status}
                                </Badge>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-gray-500">No certifications</p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t mt-4">
                      <div className="text-sm text-gray-500">
                        <span>Last Training: {record.lastTrainingDate ? format(new Date(record.lastTrainingDate), 'MMM dd, yyyy') : 'Never'}</span>
                        {record.nextRequiredTraining && (
                          <span className="mx-2">•</span>
                        )}
                        {record.nextRequiredTraining && (
                          <span>Next Required: {format(new Date(record.nextRequiredTraining), 'MMM dd, yyyy')}</span>
                        )}
                      </div>
                      <Button variant="outline" size="sm">
                        <FileText className="h-4 w-4 mr-2" />
                        Full Report
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Planning Tab */}
        <TabsContent value="planning" className="space-y-6">
          {/* Training Plan */}
          {trainingPlan && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>{trainingPlan.name}</CardTitle>
                  <CardDescription>{trainingPlan.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <h4 className="font-medium mb-3">Plan Objectives</h4>
                      <ul className="space-y-2">
                        {trainingPlan.objectives.map((objective, index) => (
                          <li key={index} className="flex items-center space-x-2">
                            <Target className="h-4 w-4 text-blue-500" />
                            <span className="text-sm">{objective}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div>
                        <h4 className="font-medium mb-2">Target Audience</h4>
                        <div className="space-y-1">
                          {trainingPlan.targetAudience.map((audience, index) => (
                            <Badge key={index} variant="outline">{audience}</Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Budget & Resources</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>Budget:</span>
                            <span>${trainingPlan.budget.toLocaleString()}</span>
                          </div>
                          <div>
                            <span className="font-medium">Resources:</span>
                            <ul className="mt-1 space-y-1">
                              {trainingPlan.resources.map((resource, index) => (
                                <li key={index} className="text-gray-600">• {resource}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Success Metrics</h4>
                        <ul className="space-y-1 text-sm">
                          {trainingPlan.successMetrics.map((metric, index) => (
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

              {/* Course Schedule */}
              <Card>
                <CardHeader>
                  <CardTitle>Course Schedule</CardTitle>
                  <CardDescription>Planned courses and training timeline</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {trainingPlan.courses.map((course) => (
                      <div key={course.courseId} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <h4 className="font-medium">{course.courseName}</h4>
                          <div className="flex items-center space-x-4 mt-2">
                            <Badge variant={course.mandatory ? 'destructive' : 'secondary'}>
                              {course.mandatory ? 'Mandatory' : 'Optional'}
                            </Badge>
                            {course.deadline && (
                              <span className="text-sm text-gray-500">
                                Due: {format(new Date(course.deadline), 'MMM dd, yyyy')}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center space-x-2 mt-2">
                            <span className="text-sm text-gray-500">Target Groups:</span>
                            <div className="flex flex-wrap gap-1">
                              {course.targetGroups.map((group, index) => (
                                <Badge key={index} variant="outline" size="sm">{group}</Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button variant="outline" size="sm">
                            <Users className="h-4 w-4 mr-2" />
                            Enroll Users
                          </Button>
                          <Button variant="outline" size="sm">
                            <BarChart3 className="h-4 w-4 mr-2" />
                            Progress
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Timeline Milestones */}
              <Card>
                <CardHeader>
                  <CardTitle>Training Milestones</CardTitle>
                  <CardDescription>Key dates and deliverables</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {trainingPlan.schedule.milestones.map((milestone, index) => (
                      <div key={index} className="flex items-start space-x-4 p-4 border rounded-lg">
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <CalendarIcon className="h-4 w-4 text-blue-600" />
                          </div>
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium">{milestone.title}</h4>
                          <p className="text-sm text-gray-600">{milestone.description}</p>
                          <span className="text-sm text-gray-500">{format(new Date(milestone.date), 'MMM dd, yyyy')}</span>
                        </div>
                        <div className="flex-shrink-0">
                          <Badge variant="outline">
                            {new Date(milestone.date) < new Date() ? 'Completed' : 'Upcoming'}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}