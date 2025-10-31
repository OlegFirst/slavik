'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { SECTIONS_NAVIGATION } from '@/lib/navigation-config'
import { ArrowRight, ExternalLink, Zap, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'

export function CentralHubEnhancements() {
  return (
    <div className="px-6 pb-6 space-y-6">
      {/* Quick Actions Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-blue-600" />
            Quick Actions
          </CardTitle>
          <CardDescription>
            Fast access to common BCM tasks and workflows
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <QuickActionCard
              title="New Risk Assessment"
              description="Start BIA or risk analysis"
              href="/sections/risk-assessment"
              icon="📊"
              badge="Popular"
            />
            <QuickActionCard
              title="Report Incident"
              description="Log crisis or emergency"
              href="/sections/incident-management"
              icon="🚨"
              badge="Critical"
              variant="destructive"
            />
            <QuickActionCard
              title="AI Analysis"
              description="Run intelligent insights"
              href="/sections/ai-automation"
              icon="🤖"
              badge="AI"
              variant="secondary"
            />
          </div>
        </CardContent>
      </Card>

      {/* Section Preview Cards */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            BCM Functional Areas
          </CardTitle>
          <CardDescription>
            Explore all business continuity management functions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {SECTIONS_NAVIGATION.slice(1).map((section) => {
              const Icon = section.icon
              return (
                <SectionPreviewCard
                  key={section.href}
                  title={section.name}
                  description={section.description || ''}
                  href={section.href}
                  icon={Icon}
                  badge={section.badge}
                />
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Cross-Module Workflow Guide */}
      <Card>
        <CardHeader>
          <CardTitle>BCM Process Workflows</CardTitle>
          <CardDescription>
            Guided workflows connecting multiple BCM functions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <WorkflowCard
              title="Complete BCM Assessment"
              description="Risk Assessment → BIA → Strategy Planning → Implementation"
              steps={["Risk Analysis", "Impact Assessment", "Plan Development", "Testing"]}
              startHref="/sections/risk-assessment"
            />
            <WorkflowCard
              title="Crisis Response Workflow"
              description="Incident Detection → Response → Recovery → Lessons Learned"
              steps={["Incident Report", "Team Activation", "Communications", "Recovery"]}
              startHref="/sections/incident-management"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

interface QuickActionCardProps {
  title: string
  description: string
  href: string
  icon: string
  badge?: string
  variant?: 'default' | 'destructive' | 'secondary'
}

function QuickActionCard({ title, description, href, icon, badge, variant = 'default' }: QuickActionCardProps) {
  return (
    <Link href={href}>
      <div className="p-4 border rounded-lg hover:shadow-md transition-all duration-200 group cursor-pointer">
        <div className="flex items-start gap-3">
          <div className="text-2xl">{icon}</div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                {title}
              </h3>
              {badge && (
                <Badge variant={variant === 'destructive' ? 'destructive' : variant === 'secondary' ? 'secondary' : 'default'}>
                  {badge}
                </Badge>
              )}
            </div>
            <p className="text-sm text-gray-500">{description}</p>
            <div className="flex items-center gap-1 mt-2 text-blue-600 text-sm">
              <span>Get started</span>
              <ArrowRight className="h-3 w-3 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}

interface SectionPreviewCardProps {
  title: string
  description: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  badge?: string
}

function SectionPreviewCard({ title, description, href, icon: Icon, badge }: SectionPreviewCardProps) {
  return (
    <Link href={href}>
      <div className="p-4 border rounded-lg hover:shadow-md transition-all duration-200 group cursor-pointer h-full">
        <div className="flex items-start gap-3 h-full">
          <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition-colors">
            <Icon className="h-5 w-5 text-gray-600 group-hover:text-blue-600 transition-colors" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors truncate">
                {title}
              </h3>
              {badge && (
                <Badge variant="secondary" className="text-xs">
                  {badge}
                </Badge>
              )}
            </div>
            <p className="text-sm text-gray-500 line-clamp-2 mb-2">{description}</p>
            <div className="flex items-center gap-1 text-blue-600 text-sm">
              <span>Explore</span>
              <ArrowRight className="h-3 w-3 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}

interface WorkflowCardProps {
  title: string
  description: string
  steps: string[]
  startHref: string
}

function WorkflowCard({ title, description, steps, startHref }: WorkflowCardProps) {
  return (
    <div className="p-4 border rounded-lg">
      <h3 className="font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-500 mb-4">{description}</p>
      
      <div className="space-y-2 mb-4">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs flex items-center justify-center font-medium">
              {index + 1}
            </div>
            <span className="text-gray-600">{step}</span>
          </div>
        ))}
      </div>
      
      <Link href={startHref}>
        <Button variant="outline" size="sm" className="w-full">
          Start Workflow
          <ArrowRight className="h-3 w-3 ml-2" />
        </Button>
      </Link>
    </div>
  )
}