'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuthStore } from '@/store/auth'
import { cn } from '@/lib/utils'
import {
  Users,
  Search,
  FileText,
  Briefcase,
  Star,
  MessageSquare,
  Settings,
  Plus
} from 'lucide-react'

const navigation = [
  { name: 'Find Specialists', href: '/specialists', icon: Search },
  { name: 'Solutions', href: '/solutions', icon: Settings },
  { name: 'Knowledge', href: '/knowledge', icon: Briefcase },
  { name: 'Case Studies', href: '/cases', icon: Star },
  { name: 'Requests', href: '/requests', icon: FileText },
]

const clientNavigation = [
  { name: 'Dashboard', href: '/client/dashboard', icon: Users },
  { name: 'Create Request', href: '/client/create-request', icon: Plus },
  { name: 'My Requests', href: '/client/requests', icon: FileText },
  { name: 'My Projects', href: '/client/projects', icon: Briefcase },
]

const specialistNavigation = [
  { name: 'My Proposals', href: '/specialist/proposals', icon: FileText },
  { name: 'My Projects', href: '/specialist/projects', icon: Briefcase },
  { name: 'My Portfolio', href: '/portfolio', icon: Star },
  { name: 'My Profile', href: '/specialist/profile', icon: Users },
]

export function Navigation() {
  const pathname = usePathname()
  const { user, isAuthenticated } = useAuthStore()

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex space-x-8">
          {/* Main Navigation */}
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center px-1 py-4 text-sm font-medium border-b-2 transition-colors',
                  isActive
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                )}
              >
                <item.icon className="mr-2 h-4 w-4" />
                {item.name}
              </Link>
            )
          })}

          {/* Role-specific Navigation */}
          {isAuthenticated && user?.role === 'client' && (
            <div className="flex items-center">
              <div className="h-6 w-px bg-gray-300 mx-4" />
              {clientNavigation.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      'flex items-center px-1 py-4 text-sm font-medium border-b-2 transition-colors ml-8',
                      isActive
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    )}
                  >
                    <item.icon className="mr-2 h-4 w-4" />
                    {item.name}
                  </Link>
                )
              })}
            </div>
          )}

          {isAuthenticated && user?.role === 'specialist' && (
            <div className="flex items-center">
              <div className="h-6 w-px bg-gray-300 mx-4" />
              {specialistNavigation.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      'flex items-center px-1 py-4 text-sm font-medium border-b-2 transition-colors ml-8',
                      isActive
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    )}
                  >
                    <item.icon className="mr-2 h-4 w-4" />
                    {item.name}
                  </Link>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}