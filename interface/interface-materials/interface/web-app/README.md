# AI-Platform-ISO Web Application

Modern, enterprise-grade web interface for the Business Continuity Management (BCM) Platform with AI Intelligence and ISO 22301 Compliance.

## Overview

This Next.js application provides a comprehensive web interface for:

- **Business Impact Analysis (BIA)** - Assess and prioritize critical business functions
- **Risk Management** - Identify, assess, and mitigate organizational risks
- **Compliance Management** - Track ISO 22301 compliance and gap analysis
- **Governance** - Decision management and tracking
- **Digital Twin** - Disruption simulation and testing
- **System Administration** - Platform monitoring and service health

## Technology Stack

### Core Framework
- **Next.js 14.2** - React framework with App Router
- **React 18** - UI library
- **TypeScript 5.3** - Type safety

### UI/UX
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **shadcn/ui** - High-quality React components (Radix UI)
- **Lucide React** - Icon library
- **next-themes** - Dark mode support

### State Management & Data Fetching
- **TanStack Query (React Query)** - Server state management
- **Zustand** - Client state management
- **Axios** - HTTP client

### Forms & Validation
- **React Hook Form** - Form management
- **Zod** - Schema validation

### Charts & Visualization
- **Recharts** - Data visualization

### Real-time
- **Socket.io Client** - WebSocket integration

### Utilities
- **date-fns** - Date manipulation
- **react-hot-toast** - Notifications
- **clsx** + **tailwind-merge** - Class name utilities

## Project Structure

```
interface/web-app/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home (redirects to dashboard)
│   │   ├── dashboard/         # Dashboard page
│   │   ├── bia/               # BIA module
│   │   ├── risk/              # Risk management module
│   │   ├── admin/             # Admin panel
│   │   └── globals.css        # Global styles
│   │
│   ├── components/            # React components
│   │   ├── ui/               # shadcn/ui base components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── input.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── progress.tsx
│   │   │   └── separator.tsx
│   │   ├── layout/           # Layout components
│   │   │   ├── sidebar.tsx
│   │   │   ├── topbar.tsx
│   │   │   └── main-layout.tsx
│   │   ├── dashboard/        # Dashboard-specific components
│   │   ├── bia/              # BIA-specific components
│   │   ├── risk/             # Risk-specific components
│   │   └── providers.tsx     # App providers
│   │
│   ├── lib/                   # Utilities and helpers
│   │   ├── api-client.ts     # API client with auth
│   │   └── utils.ts          # Utility functions
│   │
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # TypeScript type definitions
│   │   └── index.ts          # All type definitions
│   └── stores/                # Zustand state stores
│
├── public/                    # Static assets
├── .env.local.example        # Environment variables example
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── tailwind.config.ts        # Tailwind config
├── next.config.js            # Next.js config
└── README.md                 # This file
```

## Getting Started

### Prerequisites

- **Node.js**: >= 18.0.0
- **npm**: >= 9.0.0 (or yarn/pnpm)
- **Backend API**: Platform services running (default: http://localhost:8000)

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   cd /Users/MD/AI-Platform-ISO/interface/web-app
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.local.example .env.local
   ```

   Edit `.env.local` with your configuration:
   ```env
   # API Configuration
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_WS_URL=ws://localhost:8000

   # Authentication
   NEXT_PUBLIC_AUTH_ENABLED=true
   NEXT_PUBLIC_TOKEN_STORAGE_KEY=bcm_auth_token

   # Feature Flags
   NEXT_PUBLIC_ENABLE_ANALYTICS=true
   NEXT_PUBLIC_ENABLE_REALTIME=true
   NEXT_PUBLIC_ENABLE_AI_ASSISTANT=true

   # Environment
   NEXT_PUBLIC_APP_ENV=development
   NEXT_PUBLIC_APP_VERSION=2.0.0
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:3000`

### Building for Production

```bash
# Build the application
npm run build

# Start production server
npm run start

# Or preview the build
npm run preview
```

## Available Scripts

- `npm run dev` - Start development server (port 3000)
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Features

### 1. Dashboard
- **Overview Cards**: Total assessments, active risks, compliance score, critical processes
- **BCM Journey Timeline**: Visual progress tracking
- **AI Recommendations**: Intelligent insights and suggestions
- **Recent Activities**: Platform-wide activity feed
- **Risk Overview**: Distribution by severity
- **Quick Actions**: Common task shortcuts

**Route**: `/dashboard`

### 2. Business Impact Analysis (BIA)
- **Assessment Management**: Create, view, and manage BIA assessments
- **Criticality Scoring**: Visual indicators (0-10 scale)
- **Recovery Objectives**: RTO, RPO, MTPD tracking
- **Status Filtering**: Filter by draft, in-progress, completed
- **Card View**: Visual assessment cards with key metrics

**Route**: `/bia`

**Key Metrics**:
- RTO (Recovery Time Objective)
- RPO (Recovery Point Objective)
- MTPD (Maximum Tolerable Period of Disruption)
- Criticality Score

### 3. Risk Management
- **Risk Register**: Comprehensive list of identified risks
- **Risk Heat Map**: 5x5 matrix visualization (likelihood × impact)
- **Risk Scoring**: Automated calculation (likelihood × impact)
- **Category Filtering**: Strategic, operational, financial, compliance, technology, reputational
- **Status Tracking**: Identified, assessed, treated, monitored, closed
- **Mitigation Planning**: Document and track mitigation strategies

**Route**: `/risk`

**Risk Severity Levels**:
- Critical: Score 15-25 (red)
- High: Score 10-14 (orange)
- Medium: Score 5-9 (yellow)
- Low: Score 0-4 (green)

### 4. System Administration
- **Service Monitoring**: Real-time health checks for all platform services
- **Performance Metrics**: Uptime, response times, error counts
- **Service Categories**:
  - Platform Services (BIA, Risk, Compliance, Governance, Documents)
  - Intelligent Core (Workflow Intelligence, AI Foundation)
  - Infrastructure (PostgreSQL, RabbitMQ)
- **Auto-refresh**: Updates every 30 seconds

**Route**: `/admin`

### 5. Authentication & Security
- **JWT Token-based**: Secure API authentication
- **Auto-redirect**: Unauthorized users redirected to login
- **Token Storage**: LocalStorage with configurable key
- **Request Interceptors**: Automatic token injection
- **Error Handling**: Graceful error handling and user feedback

## API Integration

### API Client (`src/lib/api-client.ts`)

The application uses a centralized API client with the following features:

- **Base URL**: Configurable via environment variables
- **Authentication**: JWT bearer token
- **Interceptors**: Automatic token injection and error handling
- **Error Handling**: User-friendly error messages
- **TypeScript**: Full type safety

**Example Usage**:

```typescript
import { apiClient } from '@/lib/api-client'

// Login
await apiClient.login('user@example.com', 'password')

// Fetch data
const assessments = await apiClient.getBIAs()
const risks = await apiClient.getRisks()
const health = await apiClient.getServiceHealth()

// Create resources
const newBIA = await apiClient.createBIA({
  name: 'IT Infrastructure',
  status: 'draft',
  rto: 4,
  rpo: 1,
  mtpd: 24,
})
```

### React Query Integration

All data fetching uses React Query for:
- Automatic caching
- Background refetching
- Loading and error states
- Optimistic updates

**Example**:

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['bia', 'assessments'],
  queryFn: () => apiClient.getBIAs(),
})
```

## Component Architecture

### Base Components (shadcn/ui)

All UI components follow the shadcn/ui pattern:
- Accessible (Radix UI primitives)
- Customizable (Tailwind CSS)
- Type-safe (TypeScript)
- Consistent styling

**Available Components**:
- `Button` - Various variants and sizes
- `Card` - Content containers
- `Badge` - Status indicators
- `Progress` - Progress bars
- `Tabs` - Tabbed interfaces
- `Input` - Form inputs
- `Separator` - Visual dividers

### Layout Components

**MainLayout**:
```tsx
<MainLayout>
  <YourPageContent />
</MainLayout>
```

Includes:
- Sidebar navigation
- Top bar with search and user menu
- Responsive design
- Consistent spacing

**Sidebar**:
- Active route highlighting
- Icon navigation
- Platform version display

**Topbar**:
- Search functionality
- Notification bell
- User menu/profile

## Styling

### Tailwind CSS

The application uses Tailwind CSS with a custom design system:

**Color Palette**:
- Primary: Blue tones (BCM professional theme)
- Secondary: Gray tones
- Destructive: Red (errors, critical items)
- Success: Green (completed, healthy)
- Warning: Yellow/Orange (caution, degraded)

**Dark Mode**:
- Supported via `next-themes`
- CSS variables for easy theming
- Automatic system preference detection

### CSS Variables

Define custom colors in `globals.css`:
```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96.1%;
  /* ... */
}
```

## Type Definitions

All types are defined in `src/types/index.ts`:

**Key Types**:
- `User`, `UserRole`, `AuthResponse`
- `Organization`, `OrganizationSize`
- `BIAAssessment`, `BIAStatus`, `BusinessProcess`
- `Risk`, `RiskStatus`, `RiskCategory`, `RiskMatrixData`
- `Document`, `DocumentType`, `DocumentStatus`
- `ComplianceStatus`, `GapAnalysisItem`
- `GovernanceDecision`, `DecisionStatus`
- `DashboardSummary`, `DashboardMetrics`, `Activity`
- `ServiceHealth`, `SystemMetrics`
- `ApiResponse<T>`, `PaginatedResponse<T>`

## Development Workflow

### Adding a New Page

1. Create page file: `src/app/[route]/page.tsx`
2. Add route to sidebar: `src/components/layout/sidebar.tsx`
3. Create types if needed: `src/types/index.ts`
4. Add API methods: `src/lib/api-client.ts`

**Example**:
```tsx
// src/app/compliance/page.tsx
'use client'

import { MainLayout } from '@/components/layout/main-layout'

export default function CompliancePage() {
  return (
    <MainLayout>
      <h1>Compliance Management</h1>
      {/* Your content */}
    </MainLayout>
  )
}
```

### Adding a New Component

1. Create component: `src/components/[category]/[name].tsx`
2. Export if shared
3. Use TypeScript props interface

**Example**:
```tsx
// src/components/bia/bia-form.tsx
interface BIAFormProps {
  onSubmit: (data: BIAFormData) => void
  initialData?: BIAAssessment
}

export function BIAForm({ onSubmit, initialData }: BIAFormProps) {
  // Component logic
}
```

### Adding API Endpoints

1. Add method to `src/lib/api-client.ts`
2. Use TypeScript for request/response types
3. Handle errors appropriately

**Example**:
```typescript
async getCompliance() {
  const response = await this.client.get('/api/v1/compliance/status')
  return response.data
}
```

## Testing

### Manual Testing Checklist

- [ ] All routes accessible
- [ ] API calls successful
- [ ] Loading states display correctly
- [ ] Error handling works
- [ ] Authentication flow functional
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Dark mode toggle works
- [ ] Real-time updates functional

## Deployment

### Environment-Specific Configuration

**Development**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_ENV=development
```

**Staging**:
```env
NEXT_PUBLIC_API_URL=https://staging-api.example.com
NEXT_PUBLIC_APP_ENV=staging
```

**Production**:
```env
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_APP_ENV=production
```

### Docker Deployment

A `Dockerfile` is included in the project:

```bash
# Build image
docker build -t ai-platform-iso-ui .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://api:8000 \
  ai-platform-iso-ui
```

## Troubleshooting

### Common Issues

**1. API Connection Errors**
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify backend services are running
- Check CORS configuration

**2. Build Errors**
- Run `npm install` to ensure all dependencies are installed
- Check TypeScript errors: `npm run type-check`
- Clear Next.js cache: `rm -rf .next`

**3. Authentication Issues**
- Clear localStorage: `localStorage.clear()`
- Check token expiration
- Verify API authentication endpoints

**4. Styling Issues**
- Rebuild Tailwind: `npm run dev` (restarts build process)
- Check CSS import order
- Verify Tailwind config

## Performance Optimization

### Best Practices Implemented

- **Code Splitting**: Automatic via Next.js App Router
- **Image Optimization**: Next.js Image component
- **Lazy Loading**: React.lazy for heavy components
- **Caching**: React Query with 5-minute stale time
- **Bundle Analysis**: Run `npm run build` to see bundle sizes

### Performance Metrics Goals

- Initial Load: < 3 seconds
- Time to Interactive: < 3.5 seconds
- First Contentful Paint: < 1.5 seconds
- Lighthouse Score: > 90

## Browser Support

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Contributing

### Code Style

- Use TypeScript for all new files
- Follow ESLint rules
- Use functional components with hooks
- Prefer named exports for components
- Document complex logic with comments

### Commit Guidelines

- Use conventional commits
- Keep commits focused and atomic
- Write descriptive commit messages

## Related Documentation

- [Backend API Documentation](../../platform-services/README.md)
- [Architecture Guide](../../doc-project/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md)
- [Infrastructure Setup](../../infrastructure/README.md)

## Support

For issues and questions:
- Check existing documentation
- Review error logs
- Contact platform team

## License

Proprietary - AI-Platform-ISO

---

**Version**: 2.0.0
**Last Updated**: 2025-10-09
**Maintained By**: Frontend Team
**Status**: Production Ready
