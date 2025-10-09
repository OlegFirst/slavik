'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ChevronRight, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

interface BreadcrumbItem {
  label: string
  href: string
  icon?: React.ComponentType<{ className?: string }>
}

interface SectionBreadcrumbsProps {
  title?: string
  customItems?: BreadcrumbItem[]
  className?: string
}

export function SectionBreadcrumbs({ 
  title, 
  customItems,
  className 
}: SectionBreadcrumbsProps) {
  const pathname = usePathname()
  
  // Generate breadcrumbs from pathname if no custom items
  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const segments = pathname.split('/').filter(Boolean)
    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'Dashboard', href: '/', icon: Home }
    ]
    
    let currentPath = ''
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`
      
      // Convert segment to readable label
      let label = segment
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
      
      // Special handling for sections
      if (segment === 'sections') {
        label = 'Sections'
      } else if (segment === 'modules') {
        label = 'Modules'
      }
      
      // Use title for the last segment if provided
      if (index === segments.length - 1 && title) {
        label = title
      }
      
      breadcrumbs.push({
        label,
        href: currentPath
      })
    })
    
    return breadcrumbs
  }
  
  const breadcrumbs = customItems || generateBreadcrumbs()
  
  return (
    <nav className={cn("flex items-center space-x-1 text-sm", className)}>
      {breadcrumbs.map((item, index) => {
        const isLast = index === breadcrumbs.length - 1
        const Icon = item.icon
        
        return (
          <div key={item.href} className="flex items-center">
            {index > 0 && (
              <ChevronRight className="h-3 w-3 text-gray-400 mx-2" />
            )}
            
            {isLast ? (
              <span className="font-medium text-gray-900 flex items-center gap-1">
                {Icon && <Icon className="h-3 w-3" />}
                {item.label}
              </span>
            ) : (
              <Link
                href={item.href}
                className="text-gray-500 hover:text-gray-700 flex items-center gap-1 transition-colors"
              >
                {Icon && <Icon className="h-3 w-3" />}
                {item.label}
              </Link>
            )}
          </div>
        )
      })}
    </nav>
  )
}

// Helper to get section-specific breadcrumbs
export function getSectionBreadcrumbs(sectionId: string): BreadcrumbItem[] {
  const sectionMap: Record<string, BreadcrumbItem> = {
    'digital-twin': {
      label: 'Digital Organization Twin',
      href: '/sections/digital-twin'
    },
    'risk-assessment': {
      label: 'Risk & Impact Assessment',
      href: '/sections/risk-assessment'
    },
    'strategy-planning': {
      label: 'Strategy & Planning',
      href: '/sections/strategy-planning'
    },
    'incident-management': {
      label: 'Incident & Crisis Management',
      href: '/sections/incident-management'
    },
    'workflow-management': {
      label: 'Workflow & Process Management',
      href: '/sections/workflow-management'
    },
    'learning-community': {
      label: 'Learning & Community Hub',
      href: '/sections/learning-community'
    },
    'client-management': {
      label: 'Client & Project Management',
      href: '/sections/client-management'
    },
    'ai-automation': {
      label: 'AI & Automation Command Center',
      href: '/sections/ai-automation'
    },
    'analytics': {
      label: 'Analytics & Intelligence',
      href: '/sections/analytics'
    },
    'workspace': {
      label: 'My Workspace & Settings',
      href: '/sections/workspace'
    },
    'admin': {
      label: 'Admin Panel',
      href: '/sections/admin'
    }
  }
  
  const section = sectionMap[sectionId]
  if (!section) return []
  
  return [
    { label: 'Dashboard', href: '/', icon: Home },
    { label: 'Sections', href: '/sections' },
    section
  ]
}