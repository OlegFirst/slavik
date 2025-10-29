import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@stores/auth'
import NProgress from 'nprogress'

// Layout components
import DefaultLayout from '@components/layout/DefaultLayout.vue'

// Views - Lazy loaded for better performance
const Dashboard = () => import('@views/Dashboard.vue')
const Login = () => import('@views/auth/Login.vue')

// BCM Module Views - Mapped to actual files
const RiskAssessment = () => import('@views/modules/RiskAssessment.vue')
const BusinessImpactAnalysis = () => import('@views/modules/BCMBIA.vue')
const BCPDevelopment = () => import('@views/modules/BCMPlans.vue')
const CrisisManagement = () => import('@views/modules/BCMIncidentManagement.vue')
const IncidentManagement = () => import('@views/modules/BCMIncident.vue')
const EmergencyResponse = () => import('@views/modules/BCMExercise.vue')
const DisasterRecovery = () => import('@views/modules/BCMCore.vue')
const ComplianceManagement = () => import('@views/modules/BCMGovernance.vue')
const VendorManagement = () => import('@views/modules/BcmClients.vue')
const AssetManagement = () => import('@views/modules/BCMContext.vue')
const TrainingManagement = () => import('@views/modules/BCMTraining.vue')
const DocumentManagement = () => import('@views/modules/BCMTemplates.vue')
const AuditManagement = () => import('@views/modules/BcmAudit.vue')
const TestingExercises = () => import('@views/modules/BCMExercise.vue')
const CommunicationManagement = () => import('@views/modules/BCMPortal.vue')
const ResourceManagement = () => import('@views/modules/BCMBase.vue')
const PerformanceMetrics = () => import('@views/modules/BcmKpi.vue')
const ReportingAnalytics = () => import('@views/modules/BcmReporting.vue')
const ChangeManagement = () => import('@views/modules/BCMConfig.vue')
const AIAssistant = () => import('@views/modules/AIAssistant.vue')
const DigitalTwin = () => import('@views/modules/DigitalTwin.vue')

// Analytics Views
const Analytics = () => import('@views/Analytics.vue')

// Simulation Views
const SimulationDashboard = () => import('@views/simulation/SimulationDashboard.vue')
const ExerciseSimulation = () => import('@views/simulation/ExerciseSimulation.vue')
const SimulationResults = () => import('@views/simulation/SimulationResults.vue')

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresAuth: false,
      title: 'Login'
    }
  },
  {
    path: '/',
    component: DefaultLayout,
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: {
          title: 'Dashboard',
          icon: 'HomeIcon'
        }
      },
      // BCM Modules
      {
        path: '/risk-assessment',
        name: 'RiskAssessment',
        component: RiskAssessment,
        meta: {
          title: 'Risk Assessment',
          icon: 'ShieldExclamationIcon',
          module: 'risk'
        }
      },
      {
        path: '/business-impact-analysis',
        name: 'BusinessImpactAnalysis',
        component: BusinessImpactAnalysis,
        meta: {
          title: 'Business Impact Analysis',
          icon: 'ChartBarIcon',
          module: 'bia'
        }
      },
      {
        path: '/bcp-development',
        name: 'BCPDevelopment',
        component: BCPDevelopment,
        meta: {
          title: 'BCP Development',
          icon: 'DocumentTextIcon',
          module: 'bcp'
        }
      },
      {
        path: '/crisis-management',
        name: 'CrisisManagement',
        component: CrisisManagement,
        meta: {
          title: 'Crisis Management',
          icon: 'ExclamationTriangleIcon',
          module: 'crisis'
        }
      },
      {
        path: '/incident-management',
        name: 'IncidentManagement',
        component: IncidentManagement,
        meta: {
          title: 'Incident Management',
          icon: 'BellIcon',
          module: 'incident'
        }
      },
      {
        path: '/emergency-response',
        name: 'EmergencyResponse',
        component: EmergencyResponse,
        meta: {
          title: 'Emergency Response',
          icon: 'FireIcon',
          module: 'emergency'
        }
      },
      {
        path: '/disaster-recovery',
        name: 'DisasterRecovery',
        component: DisasterRecovery,
        meta: {
          title: 'Disaster Recovery',
          icon: 'ArrowPathIcon',
          module: 'recovery'
        }
      },
      {
        path: '/compliance-management',
        name: 'ComplianceManagement',
        component: ComplianceManagement,
        meta: {
          title: 'Compliance Management',
          icon: 'ClipboardDocumentCheckIcon',
          module: 'compliance'
        }
      },
      {
        path: '/vendor-management',
        name: 'VendorManagement',
        component: VendorManagement,
        meta: {
          title: 'Vendor Management',
          icon: 'BuildingOfficeIcon',
          module: 'vendor'
        }
      },
      {
        path: '/asset-management',
        name: 'AssetManagement',
        component: AssetManagement,
        meta: {
          title: 'Asset Management',
          icon: 'CubeIcon',
          module: 'asset'
        }
      },
      {
        path: '/training-management',
        name: 'TrainingManagement',
        component: TrainingManagement,
        meta: {
          title: 'Training Management',
          icon: 'AcademicCapIcon',
          module: 'training'
        }
      },
      {
        path: '/document-management',
        name: 'DocumentManagement',
        component: DocumentManagement,
        meta: {
          title: 'Document Management',
          icon: 'FolderIcon',
          module: 'document'
        }
      },
      {
        path: '/audit-management',
        name: 'AuditManagement',
        component: AuditManagement,
        meta: {
          title: 'Audit Management',
          icon: 'MagnifyingGlassIcon',
          module: 'audit'
        }
      },
      {
        path: '/testing-exercises',
        name: 'TestingExercises',
        component: TestingExercises,
        meta: {
          title: 'Testing & Exercises',
          icon: 'PlayIcon',
          module: 'testing'
        }
      },
      {
        path: '/communication-management',
        name: 'CommunicationManagement',
        component: CommunicationManagement,
        meta: {
          title: 'Communication Management',
          icon: 'ChatBubbleLeftRightIcon',
          module: 'communication'
        }
      },
      {
        path: '/resource-management',
        name: 'ResourceManagement',
        component: ResourceManagement,
        meta: {
          title: 'Resource Management',
          icon: 'CogIcon',
          module: 'resource'
        }
      },
      {
        path: '/performance-metrics',
        name: 'PerformanceMetrics',
        component: PerformanceMetrics,
        meta: {
          title: 'Performance Metrics',
          icon: 'ChartLineUpIcon',
          module: 'metrics'
        }
      },
      {
        path: '/reporting-analytics',
        name: 'ReportingAnalytics',
        component: ReportingAnalytics,
        meta: {
          title: 'Reporting & Analytics',
          icon: 'PresentationChartLineIcon',
          module: 'reporting'
        }
      },
      {
        path: '/change-management',
        name: 'ChangeManagement',
        component: ChangeManagement,
        meta: {
          title: 'Change Management',
          icon: 'ArrowsRightLeftIcon',
          module: 'change'
        }
      },
      {
        path: '/ai-assistant',
        name: 'AIAssistant',
        component: AIAssistant,
        meta: {
          title: 'AI Assistant',
          icon: 'SparklesIcon',
          module: 'ai'
        }
      },
      {
        path: '/digital-twin',
        name: 'DigitalTwin',
        component: DigitalTwin,
        meta: {
          title: 'Digital Twin 3D',
          icon: 'CubeIcon',
          module: 'digitaltwin'
        }
      },
      // Analytics Route
      {
        path: '/analytics',
        name: 'Analytics',
        component: Analytics,
        meta: {
          title: 'Analytics Dashboard',
          icon: 'ChartBarIcon',
          module: 'analytics'
        }
      },
      // Simulation Routes
      {
        path: '/simulation',
        name: 'SimulationDashboard',
        component: SimulationDashboard,
        meta: {
          title: 'Simulation Dashboard',
          icon: 'ComputerDesktopIcon',
          module: 'simulation'
        }
      },
      {
        path: '/simulation/exercise/:exerciseId',
        name: 'ExerciseSimulation',
        component: ExerciseSimulation,
        meta: {
          title: 'Exercise Simulation',
          icon: 'PlayIcon',
          module: 'simulation'
        },
        props: true
      },
      {
        path: '/simulation/results/:exerciseId',
        name: 'SimulationResults',
        component: SimulationResults,
        meta: {
          title: 'Simulation Results',
          icon: 'ChartBarIcon',
          module: 'simulation'
        },
        props: true
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  NProgress.start()

  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)

  // Set page title
  if (to.meta.title) {
    document.title = `${to.meta.title} - BCM Platform v2`
  }

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router