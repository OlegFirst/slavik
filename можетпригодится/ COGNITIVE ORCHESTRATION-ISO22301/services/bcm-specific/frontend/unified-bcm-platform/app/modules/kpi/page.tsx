import { KPIManagementModule } from '@/components/modules/KPIManagement'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'KPI Management - BCM Platform Analytics',
  description: 'Monitor and manage key performance indicators for business continuity processes',
}

export default function KPIManagementPage() {
  return <KPIManagementModule />
}