'use client'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { Separator } from '@/components/ui/separator'
import { ChevronRight, Zap } from 'lucide-react'

interface QuickAction {
  id: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  onClick: () => void
  variant?: 'default' | 'outline' | 'secondary' | 'destructive'
  description?: string
  badge?: string
  disabled?: boolean
  shortcut?: string
}

interface QuickActionGroup {
  title: string
  actions: QuickAction[]
}

interface QuickActionsProps {
  actions?: QuickAction[]
  groups?: QuickActionGroup[]
  title?: string
  className?: string
}

export function QuickActions({ 
  actions = [], 
  groups = [],
  title = "Quick Actions",
  className 
}: QuickActionsProps) {
  
  // If no actions or groups, don't render
  if (actions.length === 0 && groups.length === 0) return null

  // Convert simple actions to a single group if needed
  const actionGroups = groups.length > 0 ? groups : [{ title, actions }]

  return (
    <aside className={cn("w-72 bg-white border-l border-gray-200 p-4 overflow-y-auto", className)}>
      <div className="sticky top-0 bg-white pb-4">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="h-4 w-4 text-blue-600" />
          <h3 className="font-semibold text-gray-900 text-sm">{title}</h3>
        </div>
      </div>

      <div className="space-y-6">
        {actionGroups.map((group, groupIndex) => (
          <div key={groupIndex}>
            {groups.length > 1 && (
              <>
                <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
                  {group.title}
                </h4>
              </>
            )}
            
            <div className="space-y-2">
              {group.actions.map((action) => {
                const Icon = action.icon
                
                return (
                  <Button
                    key={action.id}
                    variant={action.variant || 'outline'}
                    className={cn(
                      "w-full justify-start h-auto p-3 text-left",
                      action.disabled && "opacity-50 cursor-not-allowed"
                    )}
                    onClick={action.onClick}
                    disabled={action.disabled}
                  >
                    <div className="flex items-start gap-3 w-full">
                      <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                        <Icon className="h-4 w-4" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-sm">{action.label}</span>
                          {action.shortcut && (
                            <Badge variant="secondary" className="text-xs ml-2">
                              {action.shortcut}
                            </Badge>
                          )}
                        </div>
                        
                        {action.description && (
                          <p className="text-xs text-gray-500 mt-1 text-left">
                            {action.description}
                          </p>
                        )}
                        
                        {action.badge && (
                          <Badge 
                            variant="outline" 
                            className="text-xs mt-2"
                          >
                            {action.badge}
                          </Badge>
                        )}
                      </div>
                      
                      <ChevronRight className="h-3 w-3 text-gray-400 flex-shrink-0" />
                    </div>
                  </Button>
                )
              })}
            </div>
            
            {groupIndex < actionGroups.length - 1 && (
              <Separator className="mt-4" />
            )}
          </div>
        ))}
      </div>
      
      {/* Contextual Help */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
          Need Help?
        </h4>
        <div className="space-y-2">
          <Button variant="ghost" size="sm" className="w-full justify-start">
            <span className="text-xs">📚 Documentation</span>
          </Button>
          <Button variant="ghost" size="sm" className="w-full justify-start">
            <span className="text-xs">💬 Support Chat</span>
          </Button>
          <Button variant="ghost" size="sm" className="w-full justify-start">
            <span className="text-xs">🎥 Video Tutorials</span>
          </Button>
        </div>
      </div>
    </aside>
  )
}

// Helper function to generate common quick actions for sections
export function getQuickActionsForSection(sectionId: string): QuickAction[] {
  const commonActions: Record<string, QuickAction[]> = {
    'risk-assessment': [
      {
        id: 'new-bia',
        label: 'New BIA Assessment',
        icon: ({ className }) => <div className={className}>📊</div>,
        onClick: () => console.log('New BIA'),
        description: 'Start a new Business Impact Analysis',
        shortcut: 'Ctrl+N'
      },
      {
        id: 'risk-matrix',
        label: 'View Risk Matrix',
        icon: ({ className }) => <div className={className}>🎯</div>,
        onClick: () => console.log('Risk Matrix'),
        description: 'Open interactive risk matrix'
      },
      {
        id: 'export-report',
        label: 'Export Report',
        icon: ({ className }) => <div className={className}>📄</div>,
        onClick: () => console.log('Export'),
        description: 'Generate assessment report'
      }
    ],
    'ai-automation': [
      {
        id: 'start-ai',
        label: 'Start AI Analysis',
        icon: ({ className }) => <div className={className}>🤖</div>,
        onClick: () => console.log('Start AI'),
        description: 'Run AI-powered analysis',
        badge: 'AI'
      },
      {
        id: 'automation-rules',
        label: 'Automation Rules',
        icon: ({ className }) => <div className={className}>⚙️</div>,
        onClick: () => console.log('Automation'),
        description: 'Configure automation workflows'
      }
    ],
    'incident-management': [
      {
        id: 'new-incident',
        label: 'Report Incident',
        icon: ({ className }) => <div className={className}>🚨</div>,
        onClick: () => console.log('New Incident'),
        description: 'Report a new incident',
        variant: 'destructive' as const,
        shortcut: 'Ctrl+I'
      },
      {
        id: 'activate-plan',
        label: 'Activate Plan',
        icon: ({ className }) => <div className={className}>📋</div>,
        onClick: () => console.log('Activate Plan'),
        description: 'Activate response plan'
      },
      {
        id: 'send-alert',
        label: 'Send Crisis Alert',
        icon: ({ className }) => <div className={className}>📢</div>,
        onClick: () => console.log('Send Alert'),
        description: 'Send emergency notification'
      }
    ]
  }
  
  return commonActions[sectionId] || []
}