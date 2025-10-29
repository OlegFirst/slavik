'use client'

import { SectionLayout } from '@/components/sections/SectionLayout'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { IncidentManagement } from '@/components/modules/IncidentManagement'
import { Exercise } from '@/components/modules/Exercise'
import { CrisisCommunicationHub } from '@/components/sections/CrisisCommunicationHub'
import { RecoveryCoordination } from '@/components/sections/RecoveryCoordination'
import { AlertTriangle, Radio, RotateCcw, Users } from 'lucide-react'

const sectionTabs = [
  {
    id: 'incidents',
    label: 'Incidents',
    icon: AlertTriangle,
    component: IncidentManagement,
    description: 'Incident reporting and management'
  },
  {
    id: 'exercise',
    label: 'Exercises',
    icon: Users,
    component: Exercise,
    description: 'BCM exercises and drills'
  },
  {
    id: 'crisis-comm',
    label: 'Crisis Communication',
    icon: Radio,
    component: CrisisCommunicationHub,
    description: 'Crisis communications and alerts'
  },
  {
    id: 'recovery',
    label: 'Recovery',
    icon: RotateCcw,
    component: RecoveryCoordination,
    description: 'Recovery coordination and planning'
  }
]

const relatedModules = [
  '/modules/incidents',
  '/modules/exercise',
  '/modules/crisis-comm'
]

export default function IncidentManagementSection() {
  return (
    <SectionLayout
      title="Incident & Crisis Management"
      description="Comprehensive incident response, crisis management, and recovery coordination"
      tabs={sectionTabs}
      relatedModules={relatedModules}
    />
  )
}