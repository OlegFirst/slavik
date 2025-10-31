import { AuditModule } from '@/components/modules/Audit'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Audit Management - BCM Platform Compliance',
  description: 'Manage internal and external audits, findings, and corrective actions for compliance',
}

export default function AuditPage() {
  return <AuditModule />
}