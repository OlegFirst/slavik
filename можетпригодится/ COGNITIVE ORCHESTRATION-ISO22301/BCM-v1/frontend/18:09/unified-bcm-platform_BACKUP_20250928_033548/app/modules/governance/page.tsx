import { GovernanceModule } from '@/components/modules/GovernanceModule'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Governance & Leadership - BCM Platform',
  description: 'Управление политиками, процедурами и соответствием ISO 22301',
}

export default function GovernancePage() {
  return <GovernanceModule />
}
