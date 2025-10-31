import { NextRequest, NextResponse } from 'next/server'
import { getCurrentMetrics, emitMetrics } from '@/lib/websocket/server'

// Performance tracking middleware
export function trackPerformance(req: NextRequest, startTime: number) {
  const endTime = Date.now()
  const responseTime = endTime - startTime
  
  // Extract section from URL
  const pathname = req.nextUrl.pathname
  let section = 'unknown'
  
  if (pathname.includes('/sections/risk-assessment')) section = 'risk-assessment'
  else if (pathname.includes('/sections/ai-automation')) section = 'ai-automation'
  else if (pathname.includes('/sections/analytics')) section = 'analytics'
  else if (pathname.includes('/sections/incident-management')) section = 'incident-management'
  else if (pathname.includes('/sections/strategy-planning')) section = 'strategy-planning'
  else if (pathname.includes('/sections/workspace')) section = 'workspace'
  
  // Update metrics
  const metrics = getCurrentMetrics()
  metrics.performance.requestCount++
  
  // Update section-specific metrics
  if (metrics.sections[section]) {
    metrics.sections[section].lastActivity = Date.now()
  }
  
  // Calculate rolling average response time
  if (metrics.performance.responseTime === 0) {
    metrics.performance.responseTime = responseTime
  } else {
    metrics.performance.responseTime = (metrics.performance.responseTime * 0.9) + (responseTime * 0.1)
  }
  
  console.log(`📊 ${section}: ${responseTime}ms`)
  
  return responseTime
}

// User activity tracker
export function trackUserActivity(section: string, action: 'enter' | 'exit' | 'activity') {
  const metrics = getCurrentMetrics()
  
  if (metrics.sections[section]) {
    metrics.sections[section].lastActivity = Date.now()
    
    if (action === 'enter') {
      metrics.sections[section].users++
      metrics.activeUsers++
    } else if (action === 'exit') {
      metrics.sections[section].users = Math.max(0, metrics.sections[section].users - 1)
      metrics.activeUsers = Math.max(0, metrics.activeUsers - 1)
    }
  }
  
  // Broadcast updated metrics
  emitMetrics(metrics)
}