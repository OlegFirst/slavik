import { TrainingModule } from '@/components/modules/Training'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Training Management - BCM Platform Learning',
  description: 'Manage BCM training programs, courses, and learner progress tracking',
}

export default function TrainingPage() {
  return <TrainingModule />
}