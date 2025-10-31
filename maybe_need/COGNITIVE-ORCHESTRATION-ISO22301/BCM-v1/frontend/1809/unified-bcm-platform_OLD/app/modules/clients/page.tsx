import { ClientsModule } from '@/components/modules/Clients'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Client Management - BCM Platform Relationships',
  description: 'Manage client relationships, contracts, and BCM assessments for business continuity services',
}

export default function ClientsPage() {
  return <ClientsModule />
}