'use client';

import React from 'react';

interface ExecutiveSummaryProps {
  organizationId: string;
}

interface Issue {
  critical: number;
  high: number;
  medium: number;
}

interface ReviewDate {
  id: string;
  title: string;
  date: Date;
  type: 'bia' | 'risk' | 'plan' | 'audit';
}

type ComplianceStatus = 'on-track' | 'at-risk' | 'non-compliant';

/**
 * Calculate organization health score based on multiple factors
 * Mock implementation - will be replaced with real data from API
 */
function calculateHealthScore(organizationId: string): number {
  // Mock calculation based on:
  // - BIA coverage: 30%
  // - Risk treatment status: 25%
  // - Document approval rate: 20%
  // - Incident response readiness: 15%
  // - Audit findings: 10%

  const biaCoverage = 0.9; // 90% of business units have BIA
  const riskTreatment = 0.85; // 85% of risks have treatment plans
  const documentApproval = 0.88; // 88% of required docs approved
  const incidentReadiness = 0.80; // 80% incident response capability
  const auditCompliance = 0.92; // 92% audit compliance

  const score = (
    biaCoverage * 30 +
    riskTreatment * 25 +
    documentApproval * 20 +
    incidentReadiness * 15 +
    auditCompliance * 10
  );

  return Math.round(score);
}

/**
 * Determine compliance status based on health score and critical issues
 */
function getComplianceStatus(healthScore: number, issues: Issue): ComplianceStatus {
  if (issues.critical > 0 || healthScore < 60) {
    return 'non-compliant';
  }
  if (issues.high > 3 || healthScore < 80) {
    return 'at-risk';
  }
  return 'on-track';
}

/**
 * Get outstanding issues by severity
 * Mock implementation - will fetch from API
 */
function getOutstandingIssues(organizationId: string): Issue {
  // Mock data
  return {
    critical: 2,
    high: 5,
    medium: 12
  };
}

/**
 * Get upcoming review dates
 * Mock implementation - will fetch from API
 */
function getUpcomingReviews(organizationId: string): ReviewDate[] {
  const today = new Date();

  return [
    {
      id: '1',
      title: 'IT BIA Review',
      date: new Date(today.getTime() + 5 * 24 * 60 * 60 * 1000),
      type: 'bia' as const
    },
    {
      id: '2',
      title: 'Cybersecurity Risk Assessment',
      date: new Date(today.getTime() + 12 * 24 * 60 * 60 * 1000),
      type: 'risk' as const
    },
    {
      id: '3',
      title: 'DR Plan Testing',
      date: new Date(today.getTime() + 18 * 24 * 60 * 60 * 1000),
      type: 'plan' as const
    },
    {
      id: '4',
      title: 'ISO 22301 Internal Audit',
      date: new Date(today.getTime() + 25 * 24 * 60 * 60 * 1000),
      type: 'audit' as const
    }
  ].sort((a, b) => a.date.getTime() - b.date.getTime());
}

/**
 * Format date to readable string
 */
function formatDate(date: Date): string {
  const options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric', year: 'numeric' };
  return date.toLocaleDateString('en-US', options);
}

/**
 * Get days until date
 */
function getDaysUntil(date: Date): number {
  const today = new Date();
  const diff = date.getTime() - today.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

/**
 * Get icon for review type
 */
function getReviewTypeIcon(type: ReviewDate['type']): string {
  switch (type) {
    case 'bia':
      return '📊';
    case 'risk':
      return '⚠️';
    case 'plan':
      return '📋';
    case 'audit':
      return '🔍';
    default:
      return '📅';
  }
}

/**
 * Executive Summary Component
 * Displays organization health overview with key metrics
 */
export function ExecutiveSummary({ organizationId }: ExecutiveSummaryProps) {
  const healthScore = calculateHealthScore(organizationId);
  const issues = getOutstandingIssues(organizationId);
  const complianceStatus = getComplianceStatus(healthScore, issues);
  const nextReviews = getUpcomingReviews(organizationId);

  // Calculate circle progress for health score
  const circumference = 2 * Math.PI * 45; // radius = 45
  const strokeDashoffset = circumference - (healthScore / 100) * circumference;

  // Determine health score color
  const getHealthColor = (score: number): string => {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  // Determine compliance status styling
  const getComplianceConfig = (status: ComplianceStatus) => {
    switch (status) {
      case 'on-track':
        return {
          label: 'On Track',
          color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
          icon: '✓',
          dotColor: 'bg-green-500'
        };
      case 'at-risk':
        return {
          label: 'At Risk',
          color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
          icon: '⚠',
          dotColor: 'bg-yellow-500'
        };
      case 'non-compliant':
        return {
          label: 'Non-Compliant',
          color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
          icon: '✕',
          dotColor: 'bg-red-500'
        };
    }
  };

  const complianceConfig = getComplianceConfig(complianceStatus);

  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/20 dark:to-blue-950/20 rounded-xl p-6 shadow-lg border border-purple-100 dark:border-purple-900/30">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
          Executive Summary
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Organization health and compliance overview
        </p>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Left Column: Health Score & Compliance */}
        <div className="space-y-6">

          {/* Health Score Circle */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
              Organization Health Score
            </h3>
            <div className="flex items-center justify-center">
              <div className="relative w-32 h-32">
                <svg className="transform -rotate-90 w-32 h-32">
                  {/* Background circle */}
                  <circle
                    cx="64"
                    cy="64"
                    r="45"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="transparent"
                    className="text-gray-200 dark:text-gray-700"
                  />
                  {/* Progress circle */}
                  <circle
                    cx="64"
                    cy="64"
                    r="45"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="transparent"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                    className={getHealthColor(healthScore)}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className={`text-3xl font-bold ${getHealthColor(healthScore)}`}>
                      {healthScore}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">/ 100</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-4 text-center">
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Based on BIA coverage, risk treatment, and compliance metrics
              </p>
            </div>
          </div>

          {/* Compliance Status Indicator */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
              Compliance Status
            </h3>
            <div className="flex items-center justify-center">
              <div className={`inline-flex items-center gap-3 px-6 py-4 rounded-lg ${complianceConfig.color} font-semibold text-lg`}>
                <div className={`w-3 h-3 rounded-full ${complianceConfig.dotColor} animate-pulse`}></div>
                <span>{complianceConfig.icon}</span>
                <span>{complianceConfig.label}</span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <div className="flex justify-between">
                  <span>Last Audit:</span>
                  <span className="font-medium">Oct 15, 2025</span>
                </div>
                <div className="flex justify-between">
                  <span>Next Audit:</span>
                  <span className="font-medium">Jan 20, 2026</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Issues & Reviews */}
        <div className="space-y-6">

          {/* Outstanding Issues Count */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
              Outstanding Issues
            </h3>
            <div className="space-y-3">
              {/* Critical Issues */}
              <div className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-950/20 rounded-lg border border-red-200 dark:border-red-900/30">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    Critical
                  </span>
                </div>
                <span className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {issues.critical}
                </span>
              </div>

              {/* High Issues */}
              <div className="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-950/20 rounded-lg border border-orange-200 dark:border-orange-900/30">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    High
                  </span>
                </div>
                <span className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                  {issues.high}
                </span>
              </div>

              {/* Medium Issues */}
              <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-950/20 rounded-lg border border-yellow-200 dark:border-yellow-900/30">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    Medium
                  </span>
                </div>
                <span className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                  {issues.medium}
                </span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button className="w-full text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-medium">
                View All Issues →
              </button>
            </div>
          </div>

          {/* Next Review Dates */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
              Upcoming Reviews
            </h3>
            <div className="space-y-3">
              {nextReviews.slice(0, 4).map((review) => {
                const daysUntil = getDaysUntil(review.date);
                const isUrgent = daysUntil <= 7;

                return (
                  <div
                    key={review.id}
                    className={`p-3 rounded-lg border ${
                      isUrgent
                        ? 'bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-900/30'
                        : 'bg-gray-50 dark:bg-gray-900/30 border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-2 flex-1">
                        <span className="text-lg">{getReviewTypeIcon(review.type)}</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {review.title}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                            {formatDate(review.date)}
                          </p>
                        </div>
                      </div>
                      <div className={`text-xs font-semibold px-2 py-1 rounded ${
                        isUrgent
                          ? 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300'
                          : 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300'
                      }`}>
                        {daysUntil}d
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button className="w-full text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-medium">
                View Full Calendar →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
