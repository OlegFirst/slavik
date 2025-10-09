# Quick Start Guide - AI-Platform-ISO Web UI

Get up and running in 5 minutes!

## Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000` (or configured URL)

## Installation

```bash
# Navigate to project
cd /Users/MD/AI-Platform-ISO/interface/web-app

# Install dependencies
npm install

# Setup environment
cp .env.local.example .env.local

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## What You'll See

1. **Home Page** → Redirects to Dashboard
2. **Dashboard** → Overview with stats, journey timeline, AI recommendations
3. **BIA** → Business Impact Analysis assessments
4. **Risk** → Risk register with heat map
5. **Admin** → Service health monitoring

## Key Features

### Dashboard (`/dashboard`)
- 4 KPI cards
- BCM Journey timeline
- AI Recommendations
- Recent activities
- Risk distribution
- Quick actions

### BIA (`/bia`)
- Assessment cards
- Filtering by status
- Criticality scores
- RTO/RPO/MTPD metrics

### Risk (`/risk`)
- 5×5 Risk heat map
- Risk severity badges
- Mitigation strategies
- Category filtering

### Admin (`/admin`)
- Real-time service monitoring
- Health status indicators
- Performance metrics
- Auto-refresh (30s)

## Navigation

**Sidebar Menu**:
- Dashboard
- BIA
- Risk Management
- Compliance
- Documents
- Governance
- Digital Twin
- Admin

**Topbar**:
- Search
- Notifications
- User menu

## Mock Data

The app includes mock data for development:
- All modules work without backend
- Data displays realistic BCM scenarios
- Ready for backend integration

## API Integration

**API Client** (`src/lib/api-client.ts`):
```typescript
import { apiClient } from '@/lib/api-client'

// Example usage
const assessments = await apiClient.getBIAs()
const risks = await apiClient.getRisks()
```

**Endpoints Available**:
- Authentication: login, logout, me
- Dashboard: summary, metrics, activities
- BIA: CRUD operations
- Risk: CRUD operations, matrix
- Admin: health, metrics

## Environment Variables

Edit `.env.local`:

```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# WebSocket
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Features
NEXT_PUBLIC_AUTH_ENABLED=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_REALTIME=true
```

## Common Commands

```bash
# Development
npm run dev              # Start dev server (port 3000)

# Production
npm run build           # Build for production
npm run start           # Start production server

# Code Quality
npm run lint            # Run ESLint
npm run type-check      # TypeScript checking
```

## Project Structure

```
src/
├── app/              # Pages (Next.js App Router)
│   ├── dashboard/   # Dashboard module
│   ├── bia/        # BIA module
│   ├── risk/       # Risk module
│   └── admin/      # Admin module
│
├── components/      # React components
│   ├── ui/         # Base components
│   └── layout/     # Layout components
│
├── lib/            # Utilities
│   ├── api-client.ts  # API integration
│   └── utils.ts       # Helpers
│
└── types/          # TypeScript types
    └── index.ts
```

## Technology Stack

- **Framework**: Next.js 14.2
- **UI**: React 18 + TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **Data**: React Query + Axios
- **State**: Zustand
- **Forms**: React Hook Form + Zod

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

### Module Not Found
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### API Connection Error
1. Check backend is running: `http://localhost:8000/health`
2. Verify `NEXT_PUBLIC_API_URL` in `.env.local`
3. Check browser console for errors

### Build Errors
```bash
# Clear Next.js cache
rm -rf .next

# Type check
npm run type-check

# Rebuild
npm run build
```

## Next Steps

1. **Explore** - Navigate through all modules
2. **Customize** - Modify components and styling
3. **Integrate** - Connect to real backend API
4. **Extend** - Add new features and pages

## Documentation

- **Full README**: `README.md` - Complete documentation
- **Project Summary**: `PROJECT_SUMMARY.md` - Technical details
- **This Guide**: `QUICK_START.md` - Quick reference

## Support

For detailed information:
- See `README.md` for comprehensive guide
- Check `src/types/index.ts` for all data types
- Review `src/lib/api-client.ts` for API methods

---

**Ready to build!** 🚀

Start the dev server: `npm run dev`
Open: `http://localhost:3000`
