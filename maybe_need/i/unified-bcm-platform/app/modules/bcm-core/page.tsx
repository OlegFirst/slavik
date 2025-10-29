import { BCMCoreModule } from '@/components/modules/BCMCore'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'BCM Core - Business Continuity Foundation',
  description: 'Organization context, business units, critical functions, and stakeholder management for business continuity',
}

export default function BCMCorePage() {
  return <BCMCoreModule />
}