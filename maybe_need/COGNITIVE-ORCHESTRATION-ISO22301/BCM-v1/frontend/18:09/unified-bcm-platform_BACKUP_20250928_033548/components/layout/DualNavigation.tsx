'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { 
  Home,
  Shield,
  Activity,
  ToggleLeft,
  ToggleRight,
  Building,
  Brain,
  ChevronDown,
  ExternalLink
} from 'lucide-react'
import { 
  SECTIONS_NAVIGATION, 
  MODULES_NAVIGATION, 
  getNavigationMode,
  type NavigationMode 
} from '@/lib/navigation-config'
import { useState } from 'react'

export function Sidebar() {
  const pathname = usePathname()
  const currentMode = getNavigationMode(pathname)
  const [navigationMode, setNavigationMode] = useState<NavigationMode>(currentMode)
  const [collapsedCategories, setCollapsedCategories] = useState<string[]>([])

  const toggleCategory = (category: string) => {
    setCollapsedCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    )
  }

  return (
    <div className="w-64 bg-white border-r h-screen overflow-y-auto">
      {/* Logo */}
      <div className="p-6 border-b">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-gray-900">BCM Platform</div>
            <div className="text-xs text-gray-500">Business Continuity</div>
          </div>
        </Link>
      </div>

      {/* Navigation Mode Toggle */}
      <div className="p-4 border-b">
        <div className="bg-gray-50 rounded-lg p-1 flex">
          <Button
            variant={navigationMode === 'sections' ? 'default' : 'ghost'}
            size="sm"
            className="flex-1 h-8"
            onClick={() => setNavigationMode('sections')}
          >
            <Building className="h-3 w-3 mr-1" />
            Sections
          </Button>
          <Button
            variant={navigationMode === 'modules' ? 'default' : 'ghost'}
            size="sm"
            className="flex-1 h-8"
            onClick={() => setNavigationMode('modules')}
          >
            <Brain className="h-3 w-3 mr-1" />
            Modules
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          {navigationMode === 'sections' 
            ? 'Business function view' 
            : 'Technical module view'
          }
        </p>
      </div>

      {/* Navigation Content */}
      <div className="p-4">
        {navigationMode === 'sections' ? (
          <SectionsNavigation pathname={pathname} />
        ) : (
          <ModulesNavigation 
            pathname={pathname} 
            collapsedCategories={collapsedCategories}
            onToggleCategory={toggleCategory}
          />
        )}
      </div>

      {/* Mode Switch Helper */}
      {pathname !== '/' && (
        <div className="p-4 border-t">
          <div className="text-xs text-gray-500 mb-2">Alternative View:</div>
          {pathname.startsWith('/sections/') && (
            <Link 
              href={pathname.replace('/sections/', '/modules/')}
              className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
            >
              <ExternalLink className="h-3 w-3" />
              View as Module
            </Link>
          )}
          {pathname.startsWith('/modules/') && (
            <Link 
              href={pathname.replace('/modules/', '/sections/')}
              className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
            >
              <ExternalLink className="h-3 w-3" />
              View as Section
            </Link>
          )}
        </div>
      )}
    </div>
  )
}

function SectionsNavigation({ pathname }: { pathname: string }) {
  return (
    <div className="space-y-2">
      {SECTIONS_NAVIGATION.map((section) => {
        const isActive = pathname === section.href
        const Icon = section.icon
        
        return (
          <Link
            key={section.href}
            href={section.href}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors group",
              isActive 
                ? "bg-blue-50 text-blue-700 font-medium border border-blue-200"
                : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            )}
          >
            <div className={cn(
              "w-8 h-8 rounded-lg flex items-center justify-center",
              isActive 
                ? "bg-blue-100 text-blue-600" 
                : "bg-gray-100 text-gray-600 group-hover:bg-gray-200"
            )}>
              <Icon className="h-4 w-4" />
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="truncate">{section.name}</span>
                {section.badge && (
                  <Badge variant={isActive ? "default" : "secondary"} className="text-xs">
                    {section.badge}
                  </Badge>
                )}
                {section.isNew && (
                  <Badge variant="destructive" className="text-xs">
                    New
                  </Badge>
                )}
              </div>
              {section.description && (
                <p className="text-xs text-gray-500 mt-0.5 truncate">
                  {section.description}
                </p>
              )}
            </div>
          </Link>
        )
      })}
    </div>
  )
}

function ModulesNavigation({ 
  pathname, 
  collapsedCategories, 
  onToggleCategory 
}: { 
  pathname: string
  collapsedCategories: string[]
  onToggleCategory: (category: string) => void
}) {
  return (
    <div className="space-y-6">
      {MODULES_NAVIGATION.map((category) => {
        const isCollapsed = collapsedCategories.includes(category.category)
        
        return (
          <div key={category.category}>
            <button
              onClick={() => onToggleCategory(category.category)}
              className="flex items-center justify-between w-full text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 hover:text-gray-700 transition-colors"
            >
              {category.category}
              <ChevronDown className={cn(
                "h-3 w-3 transition-transform",
                isCollapsed && "rotate-180"
              )} />
            </button>
            
            {!isCollapsed && (
              <div className="space-y-1">
                {category.items.map((module) => {
                  const isActive = pathname === module.href
                  const Icon = module.icon
                  
                  return (
                    <Link
                      key={module.href}
                      href={module.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                        isActive 
                          ? "bg-blue-50 text-blue-700 font-medium"
                          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      <span className="truncate">{module.name}</span>
                      {module.badge && (
                        <Badge variant="secondary" className="text-xs ml-auto">
                          {module.badge}
                        </Badge>
                      )}
                    </Link>
                  )
                })}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export function TopBar() {
  return (
    <div className="h-16 bg-white border-b px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold text-gray-900">BCM Platform</h1>
      </div>
      
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm">
          <Activity className="h-4 w-4 mr-2" />
          System Health
        </Button>
        <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
      </div>
    </div>
  )
}