import { IncidentManagementModule } from '@/components/modules/IncidentManagement'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Incident Management - Business Continuity Platform',
  description: 'Monitor, respond, and recover from business disruptions with comprehensive incident management',
}

export default function IncidentManagementPage() {
  return <IncidentManagementModule />
}