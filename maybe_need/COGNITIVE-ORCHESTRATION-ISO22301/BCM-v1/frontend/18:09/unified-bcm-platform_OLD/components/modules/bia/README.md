# Critical Path Analysis Component

A comprehensive React component for analyzing and visualizing business continuity recovery paths, built with TypeScript and recharts for the BCM Platform.

## Features

### 1. Visual Timeline & Gantt Chart
- **Timeline View**: Shows recovery sequence with parallel tracks
- **Gantt Chart**: Project-style visualization with dependencies
- **Time Scaling**: Switch between hours, days, and weeks
- **Criticality Color-coding**: Visual indication of task criticality levels

### 2. Resource Management
- **Resource Allocation**: Pie chart showing resource distribution
- **Utilization Tracking**: Progress bars for resource availability
- **Cost Analysis**: Detailed breakdown by resource type
- **Constraint Identification**: Highlights over-allocation issues

### 3. Critical Path Optimization
- **Bottleneck Detection**: Identifies critical constraints
- **Optimization Opportunities**: AI-suggested improvements
- **Cost-Benefit Analysis**: ROI calculations for optimizations
- **What-If Scenarios**: Model different recovery approaches

### 4. Interactive Features
- **Drag-and-Drop**: Reorder recovery sequence
- **Scenario Modeling**: Test different configurations
- **Real-time Updates**: Dynamic recalculation of metrics
- **Export Capabilities**: CSV export for further analysis

## Usage

### Basic Implementation

```tsx
import { CriticalPathAnalysis } from '@/components/modules/bia'

export default function BIAPage() {
  return (
    <div className="container mx-auto py-6">
      <CriticalPathAnalysis />
    </div>
  )
}
```

### Custom Configuration

```tsx
import { CriticalPathAnalysis } from '@/components/modules/bia'

export default function CustomBIAPage() {
  return (
    <div className="container mx-auto py-6">
      <CriticalPathAnalysis />
    </div>
  )
}
```

## Data Requirements

The component integrates with `biaAPI.getCriticalPaths()` and expects:

### Critical Path Structure
```typescript
interface CriticalPath {
  id: string
  name: string
  functions: string[]
  totalRTO: number
  bottleneckFunction: string
  optimizationOpportunities: OptimizationOpportunity[]
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
}
```

### BIA Results Structure
```typescript
interface BIAResult {
  id: string
  businessFunction: string
  department: string
  rto: number // Recovery Time Objective (hours)
  rpo: number // Recovery Point Objective (hours)
  mtpd: number // Maximum Tolerable Period of Disruption
  financialImpactPerHour: number
  criticalityLevel: 'low' | 'medium' | 'high' | 'critical'
  dependencies: string[]
  lastAssessed: string
}
```

## Key Metrics Calculated

1. **Total Recovery Time**: Sum of all critical path durations
2. **Critical Tasks**: Count of high/critical priority tasks
3. **Recovery Cost**: Total resource allocation costs
4. **Optimization Potential**: Average improvement opportunity
5. **Risk Score**: Weighted risk assessment
6. **Parallel Opportunities**: Tasks that can run concurrently

## Views and Features

### 1. Timeline View
- Visual representation of recovery sequence
- Color-coded by criticality level
- Shows task duration and dependencies
- Drag-and-drop reordering capability

### 2. Gantt Chart View
- Horizontal bar chart with task breakdown
- Resource allocation per task
- Dependency visualization
- Progress tracking capabilities

### 3. Resource View
- Pie chart of resource allocation
- Utilization bars by resource type
- Cost breakdown analysis
- Constraint identification

### 4. Optimization View
- List of improvement opportunities
- Cost-benefit analysis for each
- ROI calculations
- What-if scenario modeling

## Export Capabilities

The component provides CSV export functionality:

```typescript
// Exports include:
- Path ID and Name
- Task details (name, duration, criticality)
- Resource requirements and costs
- Dependencies and timing
- Optimization recommendations
```

## Integration with BIA API

The component automatically fetches data from:
- `biaAPI.getCriticalPaths()` - Critical path definitions
- `biaAPI.getBIAResults()` - Business function assessments

Ensure your BIA API service is configured and accessible.

## Dependencies

- **recharts**: Chart visualization library
- **@radix-ui/***: UI component primitives
- **@tanstack/react-query**: Data fetching and caching
- **lucide-react**: Icon library
- **tailwindcss**: Styling framework

## Customization

### Color Schemes
The component uses predefined color schemes for criticality levels:
- **Low**: Green (#10B981)
- **Medium**: Yellow (#F59E0B)
- **High**: Orange (#EF4444)
- **Critical**: Red (#DC2626)

### Time Scales
Support for different time perspectives:
- **Hours**: Detailed operational view
- **Days**: Weekly planning perspective
- **Weeks**: Strategic timeline view

## Performance Considerations

- Uses React.memo for expensive calculations
- Implements useMemo for data transformations
- Lazy loading for large datasets
- Optimized rendering for complex charts

## Future Enhancements

- Real-time collaboration features
- Advanced simulation capabilities
- Machine learning optimization suggestions
- Integration with external planning tools
- Mobile-responsive design improvements

## Troubleshooting

### Common Issues

1. **No data displayed**: Ensure BIA API is accessible and returns valid data
2. **Performance issues**: Check for large datasets and implement pagination
3. **Export not working**: Verify browser permissions for file downloads
4. **Charts not rendering**: Ensure recharts dependencies are properly installed

### Debug Mode

Enable debug logging by setting:
```typescript
const DEBUG_MODE = true
```

This will log data transformations and API calls to the console.