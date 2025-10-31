import { MainDashboard } from '@/components/dashboard/MainDashboard'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'BCM Platform Dashboard',
  description: 'Business Continuity Management Platform - Real-time insights and AI-powered management',
}

export default function HomePage() {
  return <MainDashboard />
}
