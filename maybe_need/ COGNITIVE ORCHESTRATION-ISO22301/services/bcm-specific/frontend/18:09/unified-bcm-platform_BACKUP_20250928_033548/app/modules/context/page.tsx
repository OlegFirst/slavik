import { ContextManagementModule } from '@/components/modules/ContextManagement'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Context Management - BCM Platform Analysis',
  description: 'Understand organizational context, stakeholders, and requirements for business continuity',
}

export default function ContextManagementPage() {
  return <ContextManagementModule />
}