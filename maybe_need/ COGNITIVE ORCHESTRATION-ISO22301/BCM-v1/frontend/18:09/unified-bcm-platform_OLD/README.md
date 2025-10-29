# Unified BCM Platform

A modern, comprehensive Business Continuity Management platform with AI-powered insights and real-time monitoring.

## Features

- **Real-time Dashboard** - Live metrics from all 28 BCM modules
- **AI Organisms Control** - Management of 10 specialized AI organs
- **Integration with Odoo** - Direct connection to BCM backend
- **Modern UI/UX** - Built with Next.js 15, React 19, and Tailwind CSS
- **Responsive Design** - Works on desktop, tablet, and mobile

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Running BCM backend (Odoo + microservices)

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The platform will be available at http://localhost:3002

### Environment Configuration

Copy `.env.local` and update the API endpoints to match your backend:

```env
NEXT_PUBLIC_API_URL=http://localhost:8069
NEXT_PUBLIC_AI_URL=http://localhost:8000
NEXT_PUBLIC_BIA_URL=http://localhost:8082
```

## Architecture

### API Integration
- **Odoo BCM Core** (port 8069) - Main business logic
- **AI Orchestrator** (port 8000) - AI organs coordination  
- **BIA Engine** (port 8082) - Business impact analysis
- **Document Processor** (port 8083) - AI document processing

### Components Structure
```
components/
├── dashboard/          # Main dashboard components
├── modules/           # Individual BCM module interfaces
├── ui/               # Reusable UI components
└── layout/           # Layout components
```

### Data Flow
1. **API Client** (`lib/api.ts`) - Handles all backend communication
2. **React Query** - Data fetching, caching, and synchronization
3. **Zustand** - Client-side state management
4. **Real-time Updates** - Automatic refresh every 30 seconds

## Development

### Adding New BCM Modules

1. Create module component in `components/modules/`
2. Add API endpoints to `lib/api.ts`
3. Create route in `app/modules/[module]/`
4. Update navigation in main layout

### API Integration

The platform automatically detects available services and gracefully degrades to mock data when services are unavailable.

### Testing

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

## Production Deployment

```bash
# Build optimized version
npm run build

# Start production server
npm start
```

## Backend Requirements

Ensure the following services are running:
- Odoo with BCM modules (port 8069)
- PostgreSQL (port 5432)
- Redis (port 6379)
- AI Orchestrator (port 8000)
- BIA Engine (port 8082)

## Support

For issues related to:
- Frontend: Check browser console and network tab
- Backend: Check Docker container logs
- API: Verify service endpoints are accessible

## License

BCM Platform - Proprietary Software
