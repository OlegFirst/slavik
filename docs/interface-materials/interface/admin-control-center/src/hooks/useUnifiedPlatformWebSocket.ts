import { useState, useEffect } from 'react'
import { io, Socket } from 'socket.io-client'

interface PlatformMetrics {
  activeUsers: number
  sections: Record<string, {
    users: number
    lastActivity: number
  }>
  performance: {
    responseTime: number
    errorCount: number
    requestCount: number
  }
  system: {
    memoryUsage: number
    cpuUsage: number
  }
}

export function useUnifiedPlatformWebSocket() {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [metrics, setMetrics] = useState<PlatformMetrics | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  useEffect(() => {
    // Try to connect to Unified Platform WebSocket
    console.log('🔄 Attempting to connect to WebSocket...')
    const newSocket = io('http://localhost:3002', {
      transports: ['websocket', 'polling'],
      timeout: 3000,
      forceNew: true
    })

    newSocket.on('connect', () => {
      console.log('🔗 Connected to Unified Platform WebSocket')
      setIsConnected(true)
    })

    newSocket.on('disconnect', () => {
      console.log('❌ Disconnected from Unified Platform WebSocket')
      setIsConnected(false)
    })

    newSocket.on('connect_error', (error) => {
      console.log('⚠️ WebSocket connection failed, using HTTP polling fallback')
      setIsConnected(false)
    })

    newSocket.on('metrics-update', (data: PlatformMetrics) => {
      console.log('📊 Received real-time metrics:', data.activeUsers, 'users')
      setMetrics(data)
      setLastUpdate(new Date())
    })

    setSocket(newSocket)

    // Cleanup on unmount
    return () => {
      newSocket.close()
    }
  }, [])

  const sendUserActivity = (section: string, action: 'enter' | 'exit' | 'activity') => {
    if (socket && isConnected) {
      socket.emit('user-activity', { section, action })
      console.log(`👤 User ${action} in ${section}`)
    }
  }

  const sendPerformanceMetric = (data: { responseTime?: number; error?: boolean }) => {
    if (socket && isConnected) {
      socket.emit('performance-metric', data)
    }
  }

  return {
    metrics,
    isConnected,
    lastUpdate,
    sendUserActivity,
    sendPerformanceMetric
  }
}