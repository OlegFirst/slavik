'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { ExternalLink, ArrowRight } from 'lucide-react'

interface RelatedModule {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  description?: string
  badge?: string
  isExternal?: boolean
}

interface RelatedModulesProps {
  modules: RelatedModule[]
  title?: string
  className?: string
}

export function RelatedModules({ 
  modules, 
  title = "Related Modules",
  className 
}: RelatedModulesProps) {
  const pathname = usePathname()

  if (modules.length === 0) return null

  return (
    <aside className={cn("w-64 bg-white border-r border-gray-200 p-4 overflow-y-auto", className)}>
      <div className="sticky top-0 bg-white pb-4">
        <h3 className="font-semibold text-gray-900 text-sm mb-4">{title}</h3>
      </div>
      
      <div className="space-y-2">
        {modules.map((module) => {
          const Icon = module.icon
          const isActive = module.href && pathname === module.href
          const isCurrentSection = pathname.startsWith('/sections/') && module.href && module.href.startsWith('/sections/')
          
          if (!module.href) return null

          return (
            <Link
              key={module.href}
              href={module.href}
              className={cn(
                "block p-3 rounded-lg border transition-all duration-200 group",
                isActive 
                  ? "bg-blue-50 border-blue-200 shadow-sm" 
                  : "bg-gray-50 border-gray-200 hover:bg-gray-100 hover:border-gray-300"
              )}
            >
              <div className="flex items-start gap-3">
                <div className={cn(
                  "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
                  isActive 
                    ? "bg-blue-100 text-blue-600" 
                    : "bg-white text-gray-600 group-hover:bg-gray-50"
                )}>
                  <Icon className="h-4 w-4" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1">
                    <span className={cn(
                      "font-medium text-sm truncate",
                      isActive ? "text-blue-900" : "text-gray-900"
                    )}>
                      {module.name}
                    </span>
                    {module.isExternal && (
                      <ExternalLink className="h-3 w-3 text-gray-400 flex-shrink-0" />
                    )}
                    {!isActive && (
                      <ArrowRight className="h-3 w-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                    )}
                  </div>
                  
                  {module.description && (
                    <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                      {module.description}
                    </p>
                  )}
                  
                  {module.badge && (
                    <Badge 
                      variant={isActive ? "default" : "secondary"} 
                      className="text-xs mt-2"
                    >
                      {module.badge}
                    </Badge>
                  )}
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      {/* Section Navigation Helper */}
      {pathname.startsWith('/sections/') && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
            Module View
          </h4>
          <Link
            href={pathname.replace('/sections/', '/modules/')}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
          >
            <ExternalLink className="h-3 w-3" />
            Switch to Module View
          </Link>
        </div>
      )}

      {/* Module Navigation Helper */}
      {pathname.startsWith('/modules/') && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
            Section View
          </h4>
          <Link
            href={pathname.replace('/modules/', '/sections/')}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
          >
            <ExternalLink className="h-3 w-3" />
            Switch to Section View
          </Link>
        </div>
      )}
    </aside>
  )
}

// Helper function to get related modules for specific sections
export function getRelatedModulesForSection(sectionId: string): RelatedModule[] {
  const relationMap: Record<string, RelatedModule[]> = {
    'risk-assessment': [
      {
        name: 'BIA Module',
        href: '/modules/bia',
        icon: ({ className }) => <div className={className}>📊</div>,
        description: 'Business Impact Analysis with AI',
        badge: 'Core'
      },
      {
        name: 'Risk Management',
        href: '/modules/risk-management',
        icon: ({ className }) => <div className={className}>🛡️</div>,
        description: 'Risk assessment and mitigation',
        badge: 'Essential'
      },
      {
        name: 'Context Management',
        href: '/modules/context',
        icon: ({ className }) => <div className={className}>🏢</div>,
        description: 'Organizational context mapping'
      }
    ],
    'ai-automation': [
      {
        name: 'AI Control Center',
        href: '/modules/ai-control',
        icon: ({ className }) => <div className={className}>🤖</div>,
        description: 'AI organisms management',
        badge: 'Core'
      },
      {
        name: 'AI Assistant',
        href: '/modules/ai-assistant',
        icon: ({ className }) => <div className={className}>🎧</div>,
        description: 'AI consulting and guidance'
      }
    ],
    'incident-management': [
      {
        name: 'Incident Management',
        href: '/modules/incidents',
        icon: ({ className }) => <div className={className}>🚨</div>,
        description: 'Crisis response and coordination',
        badge: 'Critical'
      },
      {
        name: 'Exercises',
        href: '/modules/exercises',
        icon: ({ className }) => <div className={className}>🎮</div>,
        description: 'Training exercises and drills'
      }
    ]
    // Добавлю остальные связи когда команды начнут работать
  }
  
  return relationMap[sectionId] || []
}