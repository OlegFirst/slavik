import { ComplianceDashboard } from '@/components/modules/ComplianceDashboard'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'ISO 22301 Compliance - BCM Platform',
  description: 'Мониторинг и управление соответствием стандарту ISO 22301:2019',
}

export default function CompliancePage() {
  return <ComplianceDashboard />
}
