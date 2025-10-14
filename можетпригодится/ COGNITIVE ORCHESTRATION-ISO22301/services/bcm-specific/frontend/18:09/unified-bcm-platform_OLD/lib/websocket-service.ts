import { useBCMStore } from './bcm-store'

// WebSocket message types
export interface WSMessage {
  type: 'ai_organ_update' | 'risk_alert' | 'incident_update' | 'bia_complete' | 'system_notification' | 'heartbeat'
  data: any
  timestamp: string
  source?: string
}

export interface WSConfig {
  url: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
}

// WebSocket Service Class
export class WebSocketService {
  private ws: WebSocket | null = null
  private config: WSConfig
  private reconnectTimeout: NodeJS.Timeout | null = null
  private heartbeatInterval: NodeJS.Timeout | null = null
  private messageQueue: WSMessage[] = []
  private isConnecting = false
  private listeners: Map<string, Set<(data: any) => void>> = new Map()

  constructor(config: WSConfig) {
    this.config = {
      url: config.url,
      reconnectInterval: config.reconnectInterval || 5000,
      maxReconnectAttempts: config.maxReconnectAttempts || 10,
      heartbeatInterval: config.heartbeatInterval || 30000
    }
  }

  // Connect to WebSocket server
  connect(): void {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    this.isConnecting = true
    const store = useBCMStore.getState()

    try {
      this.ws = new WebSocket(this.config.url)

      this.ws.onopen = () => {
        console.log('🔗 WebSocket connected to', this.config.url)
        this.isConnecting = false
        store.setWSConnected(true)
        store.resetWSReconnectAttempts()

        // Send queued messages
        this.flushMessageQueue()

        // Start heartbeat
        this.startHeartbeat()

        // Send initial subscription message
        this.send({
          type: 'system_notification',
          data: { action: 'subscribe', modules: ['ai_control', 'risk_management', 'bia', 'incidents'] },
          timestamp: new Date().toISOString()
        })
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason)
        this.isConnecting = false
        store.setWSConnected(false)
        this.stopHeartbeat()
        this.scheduleReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        this.isConnecting = false
        this.ws?.close()
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      this.isConnecting = false
      this.scheduleReconnect()
    }
  }

  // Schedule reconnection
  private scheduleReconnect(): void {
    const store = useBCMStore.getState()
    const attempts = store.wsReconnectAttempts

    if (attempts >= this.config.maxReconnectAttempts!) {
      console.error('Max WebSocket reconnection attempts reached')
      store.addNotification({
        type: 'error',
        title: 'Connection Lost',
        message: 'Unable to connect to server. Please refresh the page.',
        source: 'websocket-service'
      })
      return
    }

    store.incrementWSReconnectAttempts()
    const delay = Math.min(this.config.reconnectInterval! * Math.pow(2, attempts), 30000)

    console.log(`Reconnecting in ${delay}ms (attempt ${attempts + 1})...`)

    this.reconnectTimeout = setTimeout(() => {
      this.connect()
    }, delay)
  }

  // Handle incoming messages
  private handleMessage(message: WSMessage): void {
    const store = useBCMStore.getState()

    // Emit to specific listeners
    const listeners = this.listeners.get(message.type)
    if (listeners) {
      listeners.forEach(callback => callback(message.data))
    }

    // Handle different message types
    switch (message.type) {
      case 'ai_organ_update':
        this.handleAIOrganUpdate(message.data)
        break

      case 'risk_alert':
        this.handleRiskAlert(message.data)
        break

      case 'incident_update':
        this.handleIncidentUpdate(message.data)
        break

      case 'bia_complete':
        this.handleBIAComplete(message.data)
        break

      case 'system_notification':
        store.addNotification({
          type: message.data.severity || 'info',
          title: message.data.title,
          message: message.data.message,
          source: message.source || 'system'
        })
        break

      case 'heartbeat':
        // Heartbeat received, connection is alive
        break

      default:
        console.log('Unknown message type:', message.type)
    }
  }

  // Handle AI Organ updates
  private handleAIOrganUpdate(data: any): void {
    const store = useBCMStore.getState()

    if (data.organId) {
      if (data.health !== undefined) {
        store.updateAIOrganHealth(data.organId, data.health)
      }
      if (data.status !== undefined) {
        store.updateAIOrganStatus(data.organId, data.status)
      }

      // Update integration data if provided
      if (data.integration) {
        store.updateAIIntegration({
          [data.organId]: data.integration
        })
      }
    }

    // Publish module event
    store.publishEvent({
      type: 'ai_decision',
      source: 'ai-control-center',
      data: data
    })
  }

  // Handle Risk alerts
  private handleRiskAlert(data: any): void {
    const store = useBCMStore.getState()

    // Add risk to store
    store.addRisk({
      ...data,
      timestamp: new Date().toISOString(),
      source: 'websocket'
    })

    // Create notification
    store.addNotification({
      type: 'warning',
      title: 'New Risk Detected',
      message: data.description || 'A new risk has been identified',
      source: 'risk-advisor',
      actionUrl: '/modules/risk-management'
    })
  }

  // Handle Incident updates
  private handleIncidentUpdate(data: any): void {
    const store = useBCMStore.getState()

    if (data.id) {
      store.updateIncident(data.id, data)
    } else if (data.action === 'create') {
      store.addIncident(data)
    } else if (data.action === 'resolve') {
      store.resolveIncident(data.id)
    }
  }

  // Handle BIA completion
  private handleBIAComplete(data: any): void {
    const store = useBCMStore.getState()

    // Add BIA analysis to store
    store.addBIAAnalysis({
      ...data,
      timestamp: new Date().toISOString()
    })

    // Update critical functions
    if (data.criticalFunctions) {
      store.updateCriticalFunctions(data.criticalFunctions)
    }

    // Create notification
    store.addNotification({
      type: 'success',
      title: 'BIA Analysis Complete',
      message: `Analysis for ${data.functionName || 'business function'} completed`,
      source: 'bia-analyst',
      actionUrl: '/modules/bia'
    })
  }

  // Send message
  send(message: WSMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      // Queue message for later sending
      this.messageQueue.push(message)
    }
  }

  // Flush message queue
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {
      const message = this.messageQueue.shift()
      if (message) {
        this.send(message)
      }
    }
  }

  // Start heartbeat
  private startHeartbeat(): void {
    this.stopHeartbeat()
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({
          type: 'heartbeat',
          data: { timestamp: Date.now() },
          timestamp: new Date().toISOString()
        })
      }
    }, this.config.heartbeatInterval!)
  }

  // Stop heartbeat
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  // Subscribe to message type
  subscribe(type: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set())
    }
    this.listeners.get(type)!.add(callback)

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(type)
      if (listeners) {
        listeners.delete(callback)
      }
    }
  }

  // Disconnect
  disconnect(): void {
    this.stopHeartbeat()
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.messageQueue = []
    this.listeners.clear()
    useBCMStore.getState().setWSConnected(false)
  }

  // Get connection status
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  // Get WebSocket state
  getState(): number {
    return this.ws?.readyState || WebSocket.CLOSED
  }
}

// Singleton instance
let wsServiceInstance: WebSocketService | null = null

// Initialize WebSocket service
export function initWebSocketService(config?: Partial<WSConfig>): WebSocketService {
  if (!wsServiceInstance) {
    wsServiceInstance = new WebSocketService({
      url: config?.url || process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
      ...config
    })
  }
  return wsServiceInstance
}

// Get WebSocket service instance
export function getWebSocketService(): WebSocketService | null {
  return wsServiceInstance
}

// Mock WebSocket for development
export class MockWebSocket {
  private interval: NodeJS.Timeout | null = null
  private listeners: Map<string, Set<(data: any) => void>> = new Map()
  private connected = false

  connect(): void {
    this.connected = true
    useBCMStore.getState().setWSConnected(true)
    console.log('🎭 Mock WebSocket connected')

    // Start sending mock messages
    this.startMockMessages()
  }

  private startMockMessages(): void {
    this.interval = setInterval(() => {
      if (!this.connected) return

      const mockMessages = [
        {
          type: 'ai_organ_update',
          data: {
            organId: 'risk-advisor',
            health: 85 + Math.floor(Math.random() * 15),
            status: Math.random() > 0.9 ? 'idle' : 'active'
          }
        },
        {
          type: 'risk_alert',
          data: {
            id: Date.now().toString(),
            title: 'Supply Chain Risk',
            description: 'Potential disruption detected in supply chain',
            severity: 'medium',
            probability: 0.65
          }
        },
        {
          type: 'ai_organ_update',
          data: {
            organId: 'bia-analyst',
            health: 90 + Math.floor(Math.random() * 10),
            integration: {
              completedAnalyses: Math.floor(Math.random() * 10) + 40,
              criticalFunctions: 8,
              avgRTO: 4.2 + Math.random()
            }
          }
        },
        {
          type: 'system_notification',
          data: {
            title: 'System Update',
            message: 'AI models have been updated successfully',
            severity: 'info'
          }
        }
      ]

      // Send random mock message
      const message = mockMessages[Math.floor(Math.random() * mockMessages.length)]
      this.handleMessage(message as WSMessage)
    }, 5000 + Math.random() * 5000)
  }

  private handleMessage(message: WSMessage): void {
    const listeners = this.listeners.get(message.type)
    if (listeners) {
      listeners.forEach(callback => callback(message.data))
    }

    // Also handle in store
    const wsService = getWebSocketService()
    if (wsService) {
      // @ts-ignore - accessing private method for mock
      wsService.handleMessage(message)
    }
  }

  subscribe(type: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set())
    }
    this.listeners.get(type)!.add(callback)

    return () => {
      const listeners = this.listeners.get(type)
      if (listeners) {
        listeners.delete(callback)
      }
    }
  }

  send(message: WSMessage): void {
    console.log('🎭 Mock WebSocket sending:', message)
  }

  disconnect(): void {
    this.connected = false
    if (this.interval) {
      clearInterval(this.interval)
      this.interval = null
    }
    this.listeners.clear()
    useBCMStore.getState().setWSConnected(false)
    console.log('🎭 Mock WebSocket disconnected')
  }

  isConnected(): boolean {
    return this.connected
  }
}

// Export mock for development
export const mockWebSocket = new MockWebSocket()

// Auto-initialize in development mode
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  // Use mock WebSocket in development
  setTimeout(() => {
    console.log('🎭 Initializing Mock WebSocket for development')
    mockWebSocket.connect()
  }, 1000)
}