import { ReportingModule } from '@/components/modules/Reporting'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Reporting & Analytics - BCM Intelligence',
  description: 'Generate comprehensive reports and analytics from BCM data',
}

export default function ReportingPage() {
  return <ReportingModule />
}