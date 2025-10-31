import { AIControlCenterModule } from '@/components/modules/AIControlCenter'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AI Control Center - BCM Platform',
  description: 'Центр управления и мониторинга AI организма для управления непрерывностью бизнеса',
}

export default function AIControlPage() {
  return <AIControlCenterModule />
}