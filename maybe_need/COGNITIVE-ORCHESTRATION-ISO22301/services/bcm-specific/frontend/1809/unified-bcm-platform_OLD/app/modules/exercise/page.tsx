import { ExerciseModule } from '@/components/modules/Exercise'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Exercise Management - BCM Platform Testing',
  description: 'Plan, conduct, and evaluate business continuity exercises and drills',
}

export default function ExercisePage() {
  return <ExerciseModule />
}