'use client';

import React from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Users,
  FileText,
  Brain,
  Network,
  Shield,
  Zap,
  Database,
  Globe
} from 'lucide-react';
import Link from 'next/link';
import {
  RiskWidgets,
  DocumentsWidgets,
  BIAWidgets,
  QuickActionsPanel,
  ActivityTimeline,
  ExecutiveSummary
} from '@/components/dashboard';

export default function DashboardPage() {
  // TODO: Get from auth context
  const organizationId = 'org-123';
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight">Platform Dashboard</h1>
        <p className="text-muted-foreground mt-2 text-lg">
          AI-Powered ISO 22301 Business Continuity Management Platform
        </p>
      </div>

      {/* Platform Health Overview */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* Total Services */}
        <div className="rounded-xl border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Platform Services
              </p>
              <h3 className="text-3xl font-bold mt-2">46</h3>
              <p className="text-xs text-muted-foreground mt-1">
                Total microservices
              </p>
            </div>
            <div className="h-12 w-12 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <Database className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Active Services */}
        <div className="rounded-xl border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Active Services
              </p>
              <h3 className="text-3xl font-bold mt-2 text-green-600">31</h3>
              <p className="text-xs text-muted-foreground mt-1">
                Production ready
              </p>
            </div>
            <div className="h-12 w-12 rounded-lg bg-green-500/10 flex items-center justify-center">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        {/* Platform Health */}
        <div className="rounded-xl border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Platform Health
              </p>
              <h3 className="text-3xl font-bold mt-2 text-green-600">98%</h3>
              <p className="text-xs text-muted-foreground mt-1">
                Operational status
              </p>
            </div>
            <div className="h-12 w-12 rounded-lg bg-green-500/10 flex items-center justify-center">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        {/* Organizations */}
        <div className="rounded-xl border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Organizations
              </p>
              <h3 className="text-3xl font-bold mt-2">12</h3>
              <p className="text-xs text-muted-foreground mt-1">
                Multi-tenant
              </p>
            </div>
            <div className="h-12 w-12 rounded-lg bg-purple-500/10 flex items-center justify-center">
              <Users className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Executive Summary - Organization Health */}
      <ExecutiveSummary organizationId={organizationId} />

      {/* Quick Actions Panel */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
        <QuickActionsPanel />
      </div>

      {/* BCM Module Widgets - Risk Assessment */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Risk Assessment Overview</h2>
        <RiskWidgets organizationId={organizationId} />
      </div>

      {/* BCM Module Widgets - Documents */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Document Management</h2>
        <DocumentsWidgets organizationId={organizationId} />
      </div>

      {/* BCM Module Widgets - BIA */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Business Impact Analysis</h2>
        <BIAWidgets organizationId={organizationId} />
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Recent Activity</h2>
        <ActivityTimeline />
      </div>

      {/* Services Categories */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* BCM Core Services */}
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">BCM Core</h3>
              <p className="text-sm text-muted-foreground">ISO 22301 Compliance</p>
            </div>
          </div>

          <div className="space-y-3">
            <Link
              href="/bia"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <TrendingUp className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">Business Impact Analysis</span>
              </div>
              <span className="text-xs bg-green-500/10 text-green-600 px-2 py-1 rounded-full">
                Active
              </span>
            </Link>

            <Link
              href="/planning"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <FileText className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">BC Planning</span>
              </div>
              <span className="text-xs bg-green-500/10 text-green-600 px-2 py-1 rounded-full">
                Active
              </span>
            </Link>

            <Link
              href="/risk"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">Risk Management</span>
              </div>
              <span className="text-xs bg-orange-500/10 text-orange-600 px-2 py-1 rounded-full">
                Dev
              </span>
            </Link>

            <Link
              href="/learning"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Users className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">Learning & Training</span>
              </div>
              <span className="text-xs bg-green-500/10 text-green-600 px-2 py-1 rounded-full">
                Active
              </span>
            </Link>
          </div>
        </div>

        {/* Intelligence Services */}
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-600 to-cyan-600 flex items-center justify-center">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Intelligence</h3>
              <p className="text-sm text-muted-foreground">AI-Powered Services</p>
            </div>
          </div>

          <div className="space-y-3">
            <Link
              href="/digital-twin"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Network className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">Digital Twin</span>
              </div>
              <span className="text-xs bg-green-500/10 text-green-600 px-2 py-1 rounded-full">
                Active
              </span>
            </Link>

            <Link
              href="/ai"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Zap className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">AI Foundation</span>
              </div>
              <span className="text-xs bg-green-500/10 text-green-600 px-2 py-1 rounded-full">
                Active
              </span>
            </Link>

            <Link
              href="/community"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Globe className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">Community Intelligence</span>
              </div>
              <span className="text-xs bg-green-500/10 text-green-600 px-2 py-1 rounded-full">
                Active
              </span>
            </Link>

            <Link
              href="/analytics"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Activity className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">Analytics</span>
              </div>
              <span className="text-xs bg-green-500/10 text-green-600 px-2 py-1 rounded-full">
                Active
              </span>
            </Link>
          </div>
        </div>

        {/* Operations Services */}
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-green-600 to-teal-600 flex items-center justify-center">
              <CheckCircle className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Operations</h3>
              <p className="text-sm text-muted-foreground">Daily Management</p>
            </div>
          </div>

          <div className="space-y-3">
            <Link
              href="/validation"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <CheckCircle className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">Validation & Exercises</span>
              </div>
              <span className="text-xs bg-green-500/10 text-green-600 px-2 py-1 rounded-full">
                Active
              </span>
            </Link>

            <Link
              href="/documents"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <FileText className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">Documents</span>
              </div>
              <span className="text-xs bg-orange-500/10 text-orange-600 px-2 py-1 rounded-full">
                Dev
              </span>
            </Link>

            <Link
              href="/compliance"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Shield className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">Compliance</span>
              </div>
              <span className="text-xs bg-orange-500/10 text-orange-600 px-2 py-1 rounded-full">
                Dev
              </span>
            </Link>

            <Link
              href="/governance"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Users className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                <span className="font-medium">Governance</span>
              </div>
              <span className="text-xs bg-orange-500/10 text-orange-600 px-2 py-1 rounded-full">
                Dev
              </span>
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Quick Actions */}
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <h3 className="font-semibold text-lg mb-4">Quick Actions</h3>
          <div className="grid gap-3">
            <Link
              href="/bia/create"
              className="flex items-center gap-3 p-4 rounded-lg border border-dashed border-muted-foreground/30 hover:border-primary hover:bg-primary/5 transition-all group"
            >
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-medium group-hover:text-primary transition-colors">
                  Create New BIA
                </p>
                <p className="text-sm text-muted-foreground">
                  Start business impact analysis
                </p>
              </div>
            </Link>

            <Link
              href="/digital-twin/topology"
              className="flex items-center gap-3 p-4 rounded-lg border border-dashed border-muted-foreground/30 hover:border-primary hover:bg-primary/5 transition-all group"
            >
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Network className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-medium group-hover:text-primary transition-colors">
                  View Platform Topology
                </p>
                <p className="text-sm text-muted-foreground">
                  Explore service architecture
                </p>
              </div>
            </Link>

            <Link
              href="/validation/exercises/create"
              className="flex items-center gap-3 p-4 rounded-lg border border-dashed border-muted-foreground/30 hover:border-primary hover:bg-primary/5 transition-all group"
            >
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <CheckCircle className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-medium group-hover:text-primary transition-colors">
                  Run Exercise
                </p>
                <p className="text-sm text-muted-foreground">
                  Test continuity plans
                </p>
              </div>
            </Link>
          </div>
        </div>

        {/* Platform Status */}
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <h3 className="font-semibold text-lg mb-4">Platform Status</h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Services Health</span>
                <span className="text-sm font-bold text-green-600">98%</span>
              </div>
              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <div className="h-full w-[98%] bg-gradient-to-r from-green-600 to-green-400" />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">API Response Time</span>
                <span className="text-sm font-bold">245ms</span>
              </div>
              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <div className="h-full w-[75%] bg-gradient-to-r from-blue-600 to-blue-400" />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Database Performance</span>
                <span className="text-sm font-bold text-green-600">Optimal</span>
              </div>
              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <div className="h-full w-[92%] bg-gradient-to-r from-green-600 to-green-400" />
              </div>
            </div>

            <div className="pt-4 border-t">
              <Link
                href="/admin/monitoring"
                className="text-sm text-primary hover:underline font-medium"
              >
                View detailed metrics →
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Getting Started */}
      <div className="rounded-xl border bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/20 dark:to-blue-950/20 p-8">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-2xl font-bold mb-2">Welcome to AI Platform</h3>
            <p className="text-muted-foreground mb-6 max-w-2xl">
              Get started with our comprehensive Business Continuity Management platform.
              Explore modules, create analyses, and ensure your organization's resilience.
            </p>
            <div className="flex gap-4">
              <Link
                href="/organizations"
                className="px-6 py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
              >
                Manage Organizations
              </Link>
              <Link
                href="/bia"
                className="px-6 py-3 rounded-lg border bg-background font-medium hover:bg-accent transition-colors"
              >
                Start with BIA
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
