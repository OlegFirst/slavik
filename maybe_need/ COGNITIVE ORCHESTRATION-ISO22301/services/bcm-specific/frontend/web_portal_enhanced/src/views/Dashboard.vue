apply flex items-center justify-between mb-2;
}

.organism-name {
  @apply text-sm font-medium text-slate-900 dark:text-white;
}

.organism-status {
  @apply px-2 py-1 text-xs font-medium rounded-full;
  
  &.active {
    @apply bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300;
  }
  
  &.idle {
    @apply bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300;
  }
  
  &.error {
    @apply bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300;
  }
}

.organism-metrics {
  @apply space-y-2;
}

.metric {
  @apply flex items-center gap-2 text-xs;
}

.metric-label {
  @apply text-slate-600 dark:text-slate-400 min-w-0 flex-shrink-0;
}

.metric-bar {
  @apply flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden;
}

.metric-fill {
  @apply h-full bg-blue-500 transition-all duration-500;
}

.metric-value {
  @apply text-slate-700 dark:text-slate-300 font-medium min-w-0 flex-shrink-0;
}

.organism-response-time {
  @apply text-xs text-slate-500 dark:text-slate-500;
}

.organisms-footer {
  @apply border-t border-slate-200 dark:border-slate-700 pt-3 mt-4;
}

.activity-controls {
  @apply flex items-center justify-between mb-4 pb-3 border-b border-slate-200 dark:border-slate-700;
}

.activity-filters {
  @apply flex gap-2;
}

.filter-button {
  @apply px-3 py-1 text-sm rounded-full border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors;
  
  &.active {
    @apply bg-blue-100 border-blue-300 text-blue-700 dark:bg-blue-900/50 dark:border-blue-600 dark:text-blue-300;
  }
}

.activity-live-indicator {
  @apply flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-500;
  
  &.active {
    @apply text-green-600 dark:text-green-400;
  }
}

.live-dot {
  @apply w-2 h-2 rounded-full bg-slate-400 dark:bg-slate-600;
  
  .activity-live-indicator.active & {
    @apply bg-green-500 animate-pulse;
  }
}

.activity-list {
  @apply space-y-3 max-h-96 overflow-y-auto;
}

.activity-item {
  @apply flex gap-3 p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-colors;
}

.activity-icon {
  @apply flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center;
  
  &.activity-risk {
    @apply bg-red-100 text-red-600 dark:bg-red-900/50 dark:text-red-400;
  }
  
  &.activity-bcp {
    @apply bg-blue-100 text-blue-600 dark:bg-blue-900/50 dark:text-blue-400;
  }
  
  &.activity-incident {
    @apply bg-yellow-100 text-yellow-600 dark:bg-yellow-900/50 dark:text-yellow-400;
  }
  
  &.activity-training {
    @apply bg-purple-100 text-purple-600 dark:bg-purple-900/50 dark:text-purple-400;
  }
  
  &.activity-audit {
    @apply bg-green-100 text-green-600 dark:bg-green-900/50 dark:text-green-400;
  }
}

.activity-content {
  @apply flex-1 min-w-0;
}

.activity-header {
  @apply flex items-start justify-between gap-2 mb-1;
}

.activity-title {
  @apply text-sm font-medium text-slate-900 dark:text-white;
}

.activity-severity {
  @apply px-2 py-0.5 text-xs font-medium rounded-full flex-shrink-0;
  
  &.high {
    @apply bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300;
  }
  
  &.medium {
    @apply bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300;
  }
  
  &.low {
    @apply bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300;
  }
}

.activity-description {
  @apply text-sm text-slate-600 dark:text-slate-400 mb-2;
}

.activity-meta {
  @apply flex items-center gap-3 text-xs text-slate-500 dark:text-slate-500;
}

.activity-user {
  @apply font-medium;
}

.health-overview {
  @apply flex justify-center mb-6;
}

.health-circle {
  @apply w-24 h-24 rounded-full flex items-center justify-center text-center border-4 transition-all;
  
  &.healthy {
    @apply border-green-500 bg-green-50 dark:bg-green-900/20;
  }
  
  &.warning {
    @apply border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20;
  }
  
  &.critical {
    @apply border-red-500 bg-red-50 dark:bg-red-900/20;
  }
}

.health-percentage {
  @apply text-xl font-bold text-slate-900 dark:text-white;
}

.health-status-text {
  @apply text-center text-sm text-slate-600 dark:text-slate-400 mt-2;
}

.health-details {
  @apply space-y-3;
}

.health-item {
  @apply flex items-center gap-3 justify-between;
}

.health-indicator {
  @apply w-3 h-3 rounded-full bg-red-500 flex-shrink-0;
  
  &.healthy {
    @apply bg-green-500;
  }
}

.health-value {
  @apply text-sm text-slate-600 dark:text-slate-400;
}

.module-search {
  @apply mb-4;
}

.module-search-input {
  @apply w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.module-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4;
}

.module-card {
  @apply block p-4 border border-slate-200 dark:border-slate-700 rounded-lg hover:shadow-lg hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200 bg-white dark:bg-slate-800;
  
  &.disabled {
    @apply opacity-50 cursor-not-allowed;
  }
}

.module-header {
  @apply flex items-center justify-between mb-3;
}

.module-icon {
  @apply w-10 h-10 rounded-lg flex items-center justify-center;
}

.module-status {
  @apply px-2 py-1 text-xs font-medium rounded-full;
  
  &.active {
    @apply bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300;
  }
  
  &.warning {
    @apply bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300;
  }
  
  &.inactive {
    @apply bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-300;
  }
}

.module-title {
  @apply text-sm font-semibold text-slate-900 dark:text-white mb-1;
}

.module-description {
  @apply text-xs text-slate-600 dark:text-slate-400 mb-3;
}

.module-stats {
  @apply flex justify-between text-xs text-slate-500 dark:text-slate-500;
}

.quick-actions-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 gap-4;
}

.quick-action-button {
  @apply p-4 border border-slate-200 dark:border-slate-700 rounded-lg hover:shadow-md hover:border-blue-300 dark:hover:border-blue-600 transition-all text-left;
}

.action-icon {
  @apply w-8 h-8 text-blue-600 dark:text-blue-400 mb-2;
}

.action-title {
  @apply block font-semibold text-slate-900 dark:text-white mb-1;
}

.action-description {
  @apply block text-sm text-slate-600 dark:text-slate-400;
}

.risk-container {
  @apply space-y-4;
}

.risk-chart {
  @apply h-48 cursor-pointer;
  
  canvas {
    @apply w-full h-full;
  }
}

.risk-summary {
  @apply flex justify-around py-3 border-y border-slate-200 dark:border-slate-700;
}

.risk-item {
  @apply flex items-center gap-2 text-sm;
}

.risk-indicator {
  @apply w-3 h-3 rounded-full;
  
  .risk-item.high & {
    @apply bg-red-500;
  }
  
  .risk-item.medium & {
    @apply bg-yellow-500;
  }
  
  .risk-item.low & {
    @apply bg-green-500;
  }
}

.risk-actions {
  @apply flex gap-2;
}

// Responsive adjustments
@media (max-width: 768px) {
  .dashboard {
    @apply p-4;
  }
  
  .dashboard-header {
    @apply flex-col gap-4;
  }
  
  .content-grid {
    @apply grid-cols-1;
  }
  
  .kpi-grid {
    @apply grid-cols-1 sm:grid-cols-2;
  }
  
  .organisms-grid {
    @apply grid-cols-1;
  }
}

// Dark mode adjustments
@media (prefers-color-scheme: dark) {
  .dashboard {
    @apply bg-gradient-to-br from-slate-900 to-slate-800;
  }
}

// Print styles
@media print {
  .dashboard {
    @apply bg-white text-black;
  }
  
  .header-actions,
  .quick-actions-grid,
  .refresh-button {
    @apply hidden;
  }
}
</style>