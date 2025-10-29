'use client'

import { SectionLayout } from '@/components/sections/SectionLayout'
import { PersonalDashboard } from '@/components/sections/PersonalDashboard'
import { UserSettings } from '@/components/sections/UserSettings'
import { User, Settings, BarChart, Bell } from 'lucide-react'

const sectionTabs = [
  {
    id: 'dashboard',
    label: 'Personal Dashboard',
    icon: BarChart,
    component: PersonalDashboard,
    description: 'Your personal BCM overview and metrics'
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    component: UserSettings,
    description: 'User preferences and configuration'
  },
  {
    id: 'notifications',
    label: 'Notifications',
    icon: Bell,
    component: () => <div className="p-6">Notifications management coming soon...</div>,
    description: 'Manage your notification preferences'
  },
  {
    id: 'profile',
    label: 'Profile',
    icon: User,
    component: () => <div className="p-6">Profile management coming soon...</div>,
    description: 'Your profile and personal information'
  }
]

const relatedModules = [
  '/modules/configuration',
  '/modules/reporting'
]

export default function WorkspaceSection() {
  return (
    <SectionLayout
      title="My Workspace"
      description="Your personal BCM workspace with customized dashboard and settings"
      tabs={sectionTabs}
      relatedModules={relatedModules}
    />
  )
}