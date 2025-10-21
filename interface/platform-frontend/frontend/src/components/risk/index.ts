/**
 * Risk Assessment Components - Week 5 Round 3
 * Complete barrel export for all risk components
 */

// Badge Components
export {
  RiskCategoryBadge,
  getCategoryConfig,
  type RiskCategoryBadgeProps,
} from './RiskCategoryBadge';

export {
  RiskSeverityBadge,
  RiskSeverityBadgeFromScore,
  getSeverityConfig,
  type RiskSeverityBadgeProps,
  type RiskSeverityBadgeFromScoreProps,
} from './RiskSeverityBadge';

export {
  RiskStatusBadge,
  getStatusConfig,
  getStatusProgress,
  type RiskStatusBadgeProps,
} from './RiskStatusBadge';

// Form Components (Round 3 - Agent 10)
export { RiskForm } from './RiskForm';
export { RiskFilters } from './RiskFilters';
export type { RiskFilterState } from './RiskFilters';

// Treatment Plan Components
export { TreatmentPlanForm } from './TreatmentPlanForm';
export { TreatmentPlanList } from './TreatmentPlanList';

// Data Visualization Components
export { RiskMatrix } from './RiskMatrix';

// Card and List Components (Round 3 - Agent 8)
export { RiskCard, SeverityBadge } from './RiskCard';
export type { RiskCardProps } from './RiskCard';

export { RiskList } from './RiskList';
export type { RiskListProps, FilterState, SortOption } from './RiskList';

// Advanced Analysis Components (Round 3 - Agent 11)
export { FAIRAnalysisCard } from './FAIRAnalysisCard';
export { MonteCarloChart } from './MonteCarloChart';
