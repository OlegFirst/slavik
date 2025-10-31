'use client'

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { RelatedModules } from './RelatedModules'
import { QuickActions } from './QuickActions'
import { SectionBreadcrumbs } from './SectionBreadcrumbs'
import { ChevronLeft, ExternalLink } from 'lucide-react'
import Link from 'next/link'

interface SectionTab {
  id: string
  label: string
  icon?: React.ComponentType<{ className?: string }>
  component: ReactNode
}

interface QuickAction {
  id: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  onClick: () => void
  variant?: 'default' | 'outline' | 'secondary'
}

interface RelatedModule {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  description?: string
}

interface SectionLayoutProps {
  title: string
  description?: string
  children?: ReactNode
  tabs?: SectionTab[]
  defaultTab?: string
  relatedModules?: RelatedModule[]
  quickActions?: QuickAction[]
  className?: string
  backButton?: {
    href: string
    label: string
  }
  headerActions?: ReactNode
  showRelatedModules?: boolean
  showQuickActions?: boolean
}

export function SectionLayout({
  title,
  description,
  children,
  tabs,
  defaultTab,
  relatedModules = [],
  quickActions = [],
  className,
  backButton,
  headerActions,
  showRelatedModules = true,
  showQuickActions = true
}: SectionLayoutProps) {
  
  const hasLeftSidebar = showRelatedModules && relatedModules.length > 0
  const hasRightSidebar = showQuickActions && quickActions.length > 0

  return (
    <div className={cn("min-h-screen bg-gray-50", className)}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="px-6 py-4">
          {/* Breadcrumbs */}
          <SectionBreadcrumbs title={title} />
          
          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center gap-4">
              {backButton && (
                <Link href={backButton.href}>
                  <Button variant="ghost" size="sm">
                    <ChevronLeft className="h-4 w-4 mr-1" />
                    {backButton.label}
                  </Button>
                </Link>
              )}
              
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
                {description && (
                  <p className="text-gray-600 mt-1">{description}</p>
                )}
              </div>
            </div>
            
            {headerActions && (
              <div className="flex items-center gap-2">
                {headerActions}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-120px)]">
        {/* Left Sidebar - Related Modules */}
        {hasLeftSidebar && (
          <RelatedModules modules={relatedModules} />
        )}

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6">
            {tabs ? (
              <Tabs defaultValue={defaultTab || tabs[0]?.id} className="w-full">
                <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:grid-cols-none lg:flex">
                  {tabs.map((tab) => {
                    const Icon = tab.icon
                    return (
                      <TabsTrigger 
                        key={tab.id} 
                        value={tab.id}
                        className="flex items-center gap-2"
                      >
                        {Icon && <Icon className="h-4 w-4" />}
                        {tab.label}
                      </TabsTrigger>
                    )
                  })}
                </TabsList>
                
                {tabs.map((tab) => (
                  <TabsContent key={tab.id} value={tab.id} className="mt-6">
                    {tab.component}
                  </TabsContent>
                ))}
              </Tabs>
            ) : (
              children
            )}
          </div>
        </div>

        {/* Right Sidebar - Quick Actions */}
        {hasRightSidebar && (
          <QuickActions actions={quickActions} />
        )}
      </div>
    </div>
  )
}

// Utility component for tab content wrapper
export function SectionTabContent({ 
  children, 
  className 
}: { 
  children: ReactNode
  className?: string 
}) {
  return (
    <div className={cn("space-y-6", className)}>
      {children}
    </div>
  )
}

// Pre-built section header for consistency
export function SectionHeader({
  title,
  description,
  children
}: {
  title: string
  description?: string
  children?: ReactNode
}) {
  return (
    <div className="flex items-center justify-between mb-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        {description && (
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        )}
      </div>
      {children && (
        <div className="flex items-center gap-2">
          {children}
        </div>
      )}
    </div>
  )
}