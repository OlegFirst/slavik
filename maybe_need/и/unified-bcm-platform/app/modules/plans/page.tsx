import { PlansManagementModule } from '@/components/modules/PlansManagement'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Plans Management - Business Continuity Planning',
  description: 'Create, maintain and test comprehensive business continuity plans',
}

export default function PlansManagementPage() {
  return <PlansManagementModule />
}