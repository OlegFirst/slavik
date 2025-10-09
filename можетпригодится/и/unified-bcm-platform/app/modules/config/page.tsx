import { ConfigurationModule } from '@/components/modules/Configuration'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'System Configuration - BCM Platform Administration',
  description: 'Manage system settings, users, integrations and security configuration',
}

export default function ConfigurationPage() {
  return <ConfigurationModule />
}