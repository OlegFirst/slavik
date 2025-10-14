import { Server } from 'socket.io'
import type { Server as HTTPServer } from 'http'

let io: Server | null = null

// Metrics store
let platformMetrics = {
  activeUsers: 0,
  sections: {
    'risk-assessment': { users: 0, lastActivity: Date.now() },
    'ai-automation': { users: 0, lastActivity: Date.now() },
    'analytics': { users: 0, lastActivity: Date.now() },
    'incident-management': { users: 0, lastActivity: Date.now() },
    'strategy-planning': { users: 0, lastActivity: Date.now() },
    'workspace': { users: 0, lastActivity: Date.now() }
  },
  performance: {
    responseTime: 0,
    errorCount: 0,
    requestCount: 0
  },
  system: {
    memoryUsage: 0,
    cpuUsage: 0
  }
}

export function initWebSocket(server: HTTPServer) {
  io = new Server(server, {
    cors: {
      origin: ["http://localhost:3001"], // Admin Panel URL
      methods: ["GET", "POST"]
    }
  })

  io.on('connection', (socket) => {
    console.log('📡 Admin Panel connected to WebSocket')
    
    // Send current metrics on connection
    socket.emit('metrics-update', platformMetrics)
    
    // Handle user activity tracking
    socket.on('user-activity', (data) => {
      updateUserActivity(data.section, data.action)
    })
    
    // Handle performance metrics
    socket.on('performance-metric', (data) => {
      updatePerformanceMetrics(data)
    })
    
    socket.on('disconnect', () => {
      console.log('📡 Admin Panel disconnected from WebSocket')
    })
  })

  // Send metrics every 5 seconds
  setInterval(() => {
    if (io) {
      // Update system metrics
      updateSystemMetrics()
      io.emit('metrics-update', platformMetrics)
    }
  }, 5000)

  return io
}

function updateUserActivity(section: string, action: string) {
  if (platformMetrics.sections[section]) {
    platformMetrics.sections[section].lastActivity = Date.now()
    
    // Increment user count for active sections
    if (action === 'enter') {
      platformMetrics.sections[section].users++
      platformMetrics.activeUsers++
    } else if (action === 'exit') {
      platformMetrics.sections[section].users = Math.max(0, platformMetrics.sections[section].users - 1)
      platformMetrics.activeUsers = Math.max(0, platformMetrics.activeUsers - 1)
    }
  }
}

function updatePerformanceMetrics(data: any) {
  platformMetrics.performance.requestCount++
  
  if (data.responseTime) {
    // Calculate rolling average
    platformMetrics.performance.responseTime = 
      (platformMetrics.performance.responseTime * 0.9) + (data.responseTime * 0.1)
  }
  
  if (data.error) {
    platformMetrics.performance.errorCount++
  }
}

function updateSystemMetrics() {
  // Get real system metrics (Node.js process)
  const memUsage = process.memoryUsage()
  const cpuUsage = process.cpuUsage()
  
  platformMetrics.system.memoryUsage = Math.round((memUsage.heapUsed / memUsage.heapTotal) * 100)
  platformMetrics.system.cpuUsage = Math.round(Math.random() * 30 + 15) // Simulated CPU for now
  
  // Clean up inactive sessions (older than 5 minutes)
  const fiveMinutesAgo = Date.now() - 5 * 60 * 1000
  let totalUsers = 0
  
  Object.keys(platformMetrics.sections).forEach(section => {
    const sectionData = platformMetrics.sections[section]
    if (sectionData.lastActivity < fiveMinutesAgo) {
      sectionData.users = Math.max(0, sectionData.users - 1)
    }
    totalUsers += sectionData.users
  })
  
  platformMetrics.activeUsers = totalUsers
}

export function emitMetrics(metrics: any) {
  if (io) {
    io.emit('metrics-update', metrics)
  }
}

export function getCurrentMetrics() {
  return platformMetrics
}