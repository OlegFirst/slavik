import { MainDashboard } from '@/components/dashboard/MainDashboard'
import { CentralHubEnhancements } from '@/components/sections/CentralHubEnhancements'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'BCM Platform - Central Hub',
  description: 'Business Continuity Management Platform - Multi-tenant overview with unified access to all BCM functions',
}

export default function HomePage() {
  return (
    <div className="space-y-6">
      {/* Existing Main Dashboard */}
      <MainDashboard />
      
      {/* New Central Hub Enhancements */}
      <CentralHubEnhancements />
    </div>
  )
}