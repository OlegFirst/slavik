import { create } from 'zustand'
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware'

// Types for AI Organ Integration
export interface AIOrganIntegration {
  riskAdvisor: {
    activeRisks: number
    lastAnalysis: string
    recommendations: string[]
  }
  biaAnalyst: {
    completedAnalyses: number
    criticalFunctions: number
    avgRTO: number
  }
  incidentCommander: {
    activeIncidents: number
    responseTeams: number
    avgResponseTime: number
  }
  governanceBrain: {
    policies: number
    compliance: number
    strategicGoals: number
  }
}

// Types for notifications
export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error' | 'ai'
  title: string
  message: string
  source: string
  timestamp: Date
  read: boolean
  actionUrl?: string
}

// Types for cross-module events
export interface ModuleEvent {
  id: string
  type: 'risk_detected' | 'bia_completed' | 'incident_created' | 'ai_decision' | 'system_alert'
  source: string
  target?: string
  data: any
  timestamp: Date
}

// Main store state interface
interface BCMStore {
  // AI Organs state
  aiOrgansHealth: { [key: string]: number }
  aiOrgansStatus: { [key: string]: 'active' | 'idle' | 'error' | 'maintenance' }
  aiIntegration: AIOrganIntegration

  // Cross-module shared data
  activeRisks: any[]
  criticalFunctions: any[]
  activeIncidents: any[]
  recentBIAAnalyses: any[]

  // Notifications
  notifications: Notification[]
  unreadCount: number

  // Module events for event-driven architecture
  moduleEvents: ModuleEvent[]

  // WebSocket connection state
  wsConnected: boolean
  wsReconnectAttempts: number

  // Actions
  updateAIOrganHealth: (organId: string, health: number) => void
  updateAIOrganStatus: (organId: string, status: 'active' | 'idle' | 'error' | 'maintenance') => void
  updateAIIntegration: (data: Partial<AIOrganIntegration>) => void

  // Risk Management actions
  addRisk: (risk: any) => void
  updateRisk: (riskId: string, data: any) => void
  removeRisk: (riskId: string) => void

  // BIA actions
  addBIAAnalysis: (analysis: any) => void
  updateCriticalFunctions: (functions: any[]) => void

  // Incident actions
  addIncident: (incident: any) => void
  updateIncident: (incidentId: string, data: any) => void
  resolveIncident: (incidentId: string) => void

  // Notification actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void
  markNotificationAsRead: (notificationId: string) => void
  markAllNotificationsAsRead: () => void
  clearNotifications: () => void

  // Module event actions
  publishEvent: (event: Omit<ModuleEvent, 'id' | 'timestamp'>) => void
  subscribeToEvents: (callback: (event: ModuleEvent) => void) => () => void

  // WebSocket actions
  setWSConnected: (connected: boolean) => void
  incrementWSReconnectAttempts: () => void
  resetWSReconnectAttempts: () => void
}

// Event subscribers storage
const eventSubscribers = new Set<(event: ModuleEvent) => void>()

// Create the store
export const useBCMStore = create<BCMStore>()(
  devtools(
    persist(
      subscribeWithSelector((set, get) => ({
        // Initial state
        aiOrgansHealth: {
          'governance-brain': 95,
          'risk-advisor': 88,
          'incident-commander': 92,
          'training-mentor': 90,
          'audit-inspector': 87,
          'recovery-planner': 85,
          'communication-hub': 93,
          'resource-manager': 89,
          'performance-monitor': 91,
          'knowledge-keeper': 94
        },

        aiOrgansStatus: {
          'governance-brain': 'active',
          'risk-advisor': 'active',
          'incident-commander': 'active',
          'training-mentor': 'active',
          'audit-inspector': 'active',
          'recovery-planner': 'active',
          'communication-hub': 'active',
          'resource-manager': 'idle',
          'performance-monitor': 'active',
          'knowledge-keeper': 'active'
        },

        aiIntegration: {
          riskAdvisor: {
            activeRisks: 12,
            lastAnalysis: '2 минуты назад',
            recommendations: [
              'Обновить план реагирования на кибер-риски',
              'Провести тренинг по эвакуации',
              'Пересмотреть договоры с поставщиками'
            ]
          },
          biaAnalyst: {
            completedAnalyses: 45,
            criticalFunctions: 8,
            avgRTO: 4.2
          },
          incidentCommander: {
            activeIncidents: 2,
            responseTeams: 3,
            avgResponseTime: 15
          },
          governanceBrain: {
            policies: 24,
            compliance: 94,
            strategicGoals: 7
          }
        },

        activeRisks: [],
        criticalFunctions: [],
        activeIncidents: [],
        recentBIAAnalyses: [],
        notifications: [],
        unreadCount: 0,
        moduleEvents: [],
        wsConnected: false,
        wsReconnectAttempts: 0,

        // AI Organ actions
        updateAIOrganHealth: (organId, health) => set((state) => ({
          aiOrgansHealth: {
            ...state.aiOrgansHealth,
            [organId]: health
          }
        })),

        updateAIOrganStatus: (organId, status) => set((state) => ({
          aiOrgansStatus: {
            ...state.aiOrgansStatus,
            [organId]: status
          }
        })),

        updateAIIntegration: (data) => set((state) => ({
          aiIntegration: {
            ...state.aiIntegration,
            ...data
          }
        })),

        // Risk Management actions
        addRisk: (risk) => {
          set((state) => ({
            activeRisks: [...state.activeRisks, { ...risk, id: Date.now().toString() }]
          }))
          get().publishEvent({
            type: 'risk_detected',
            source: 'risk-management',
            data: risk
          })
        },

        updateRisk: (riskId, data) => set((state) => ({
          activeRisks: state.activeRisks.map(r => r.id === riskId ? { ...r, ...data } : r)
        })),

        removeRisk: (riskId) => set((state) => ({
          activeRisks: state.activeRisks.filter(r => r.id !== riskId)
        })),

        // BIA actions
        addBIAAnalysis: (analysis) => {
          set((state) => ({
            recentBIAAnalyses: [
              { ...analysis, id: Date.now().toString(), timestamp: new Date() },
              ...state.recentBIAAnalyses.slice(0, 9)
            ]
          }))
          get().publishEvent({
            type: 'bia_completed',
            source: 'bia-module',
            data: analysis
          })
        },

        updateCriticalFunctions: (functions) => set(() => ({
          criticalFunctions: functions
        })),

        // Incident actions
        addIncident: (incident) => {
          set((state) => ({
            activeIncidents: [...state.activeIncidents, {
              ...incident,
              id: Date.now().toString(),
              status: 'active'
            }]
          }))
          get().publishEvent({
            type: 'incident_created',
            source: 'incident-management',
            data: incident
          })
          get().addNotification({
            type: 'warning',
            title: 'Новый инцидент',
            message: incident.description || 'Создан новый инцидент',
            source: 'incident-management'
          })
        },

        updateIncident: (incidentId, data) => set((state) => ({
          activeIncidents: state.activeIncidents.map(i =>
            i.id === incidentId ? { ...i, ...data } : i
          )
        })),

        resolveIncident: (incidentId) => set((state) => ({
          activeIncidents: state.activeIncidents.map(i =>
            i.id === incidentId ? { ...i, status: 'resolved' } : i
          )
        })),

        // Notification actions
        addNotification: (notification) => set((state) => {
          const newNotification: Notification = {
            ...notification,
            id: Date.now().toString(),
            timestamp: new Date(),
            read: false
          }
          return {
            notifications: [newNotification, ...state.notifications],
            unreadCount: state.unreadCount + 1
          }
        }),

        markNotificationAsRead: (notificationId) => set((state) => {
          const notification = state.notifications.find(n => n.id === notificationId)
          if (!notification || notification.read) return state

          return {
            notifications: state.notifications.map(n =>
              n.id === notificationId ? { ...n, read: true } : n
            ),
            unreadCount: Math.max(0, state.unreadCount - 1)
          }
        }),

        markAllNotificationsAsRead: () => set((state) => ({
          notifications: state.notifications.map(n => ({ ...n, read: true })),
          unreadCount: 0
        })),

        clearNotifications: () => set(() => ({
          notifications: [],
          unreadCount: 0
        })),

        // Module event actions
        publishEvent: (event) => {
          const fullEvent: ModuleEvent = {
            ...event,
            id: Date.now().toString(),
            timestamp: new Date()
          }

          set((state) => ({
            moduleEvents: [fullEvent, ...state.moduleEvents.slice(0, 99)]
          }))

          // Notify all subscribers
          eventSubscribers.forEach(callback => callback(fullEvent))
        },

        subscribeToEvents: (callback) => {
          eventSubscribers.add(callback)
          return () => eventSubscribers.delete(callback)
        },

        // WebSocket actions
        setWSConnected: (connected) => set(() => ({
          wsConnected: connected
        })),

        incrementWSReconnectAttempts: () => set((state) => ({
          wsReconnectAttempts: state.wsReconnectAttempts + 1
        })),

        resetWSReconnectAttempts: () => set(() => ({
          wsReconnectAttempts: 0
        }))
      })),
      {
        name: 'bcm-store',
        partialize: (state) => ({
          // Persist only essential data
          notifications: state.notifications.slice(0, 50),
          aiOrgansHealth: state.aiOrgansHealth,
          aiOrgansStatus: state.aiOrgansStatus
        })
      }
    )
  )
)

// Selectors for common queries
export const selectActiveRisksCount = (state: BCMStore) =>
  state.activeRisks.filter(r => r.status === 'active').length

export const selectCriticalIncidentsCount = (state: BCMStore) =>
  state.activeIncidents.filter(i => i.priority === 'critical' && i.status === 'active').length

export const selectOverallSystemHealth = (state: BCMStore) => {
  const healths = Object.values(state.aiOrgansHealth)
  return Math.round(healths.reduce((a, b) => a + b, 0) / healths.length)
}

export const selectActiveAIOrgansCount = (state: BCMStore) =>
  Object.values(state.aiOrgansStatus).filter(s => s === 'active').length

// WebSocket connection helper
export const initWebSocket = (url: string = 'ws://localhost:8000/ws') => {
  let ws: WebSocket | null = null
  let reconnectTimeout: NodeJS.Timeout | null = null

  const connect = () => {
    try {
      ws = new WebSocket(url)

      ws.onopen = () => {
        console.log('WebSocket connected')
        useBCMStore.getState().setWSConnected(true)
        useBCMStore.getState().resetWSReconnectAttempts()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleWebSocketMessage(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        useBCMStore.getState().setWSConnected(false)
        reconnect()
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        ws?.close()
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      reconnect()
    }
  }

  const reconnect = () => {
    const attempts = useBCMStore.getState().wsReconnectAttempts
    if (attempts >= 10) {
      console.error('Max WebSocket reconnection attempts reached')
      return
    }

    useBCMStore.getState().incrementWSReconnectAttempts()
    const delay = Math.min(1000 * Math.pow(2, attempts), 30000)

    reconnectTimeout = setTimeout(() => {
      console.log(`Attempting to reconnect WebSocket (attempt ${attempts + 1})...`)
      connect()
    }, delay)
  }

  const handleWebSocketMessage = (message: any) => {
    const store = useBCMStore.getState()

    switch (message.type) {
      case 'ai_organ_update':
        if (message.data.health !== undefined) {
          store.updateAIOrganHealth(message.data.organId, message.data.health)
        }
        if (message.data.status !== undefined) {
          store.updateAIOrganStatus(message.data.organId, message.data.status)
        }
        break

      case 'risk_alert':
        store.addRisk(message.data)
        store.addNotification({
          type: 'warning',
          title: 'Новый риск обнаружен',
          message: message.data.description,
          source: 'risk-advisor'
        })
        break

      case 'incident_update':
        if (message.data.id) {
          store.updateIncident(message.data.id, message.data)
        }
        break

      case 'bia_complete':
        store.addBIAAnalysis(message.data)
        store.addNotification({
          type: 'success',
          title: 'BIA анализ завершен',
          message: `Анализ для ${message.data.functionName} завершен`,
          source: 'bia-analyst'
        })
        break

      case 'system_notification':
        store.addNotification(message.data)
        break

      default:
        console.log('Unknown WebSocket message type:', message.type)
    }
  }

  // Start connection
  connect()

  // Return cleanup function
  return () => {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
    }
    if (ws) {
      ws.close()
    }
  }
}

export default useBCMStore