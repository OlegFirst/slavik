import { RiskManagementModule } from '@/components/modules/RiskManagement'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Risk Management - BCM Platform',
  description: 'AI-powered risk assessment and management system',
}

export default function RiskManagementPage() {
  return <RiskManagementModule />
}
