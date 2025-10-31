'use client'

import { DependencyMap } from '@/components/modules/bia/DependencyMap'
import { Metadata } from 'next'

export default function DependencyMapPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <DependencyMap />
    </div>
  )
}