import { BIAModule } from '@/components/modules/BIAModule'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Business Impact Analysis - BCM Platform',
  description: 'AI-powered Business Impact Analysis with ML-enhanced BIA Engine v2.0',
}

export default function BIAPage() {
  return <BIAModule />
}
