import { TemplatesModule } from '@/components/modules/Templates'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Template Management - BCM Platform Documents',
  description: 'Create, manage, and use standardized BCM document templates and forms',
}

export default function TemplatesPage() {
  return <TemplatesModule />
}