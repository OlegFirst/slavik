# 🎯 Digital Twin - Frontend

**Next.js 14 application for BCM Digital Twin Platform**

---

## 🚀 Quick Start

### Development Mode:

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Open browser
open http://localhost:3000
```

**Login:** admin / admin

---

## 📦 Stack

- **Next.js 14** (App Router)
- **TypeScript**
- **TailwindCSS**
- **TanStack Query** (React Query)
- **Zustand** (state management)
- **axios** (HTTP client)
- **react-hook-form** + zod (forms + validation)
- **lucide-react** (icons)

---

## 🎨 Features Implemented

### ✅ Authentication
- JWT-based login/logout
- Protected routes
- Token management

### ✅ AI Insights Dashboard
- Organization selector
- Real-time AI insights
- Color-coded by impact
- Confidence meters
- Suggested actions

### ✅ Queue Theory BIA
- Comprehensive input form (λ, μ, c parameters)
- Results visualization
- RTO/RPO recommendations
- Recovery strategies table
- Financial impact analysis

### ✅ AI Scenario Generator
- AI-powered scenario generation
- Complexity slider (1-10)
- Focus areas (keywords)
- Historical context toggle
- Generated scenario display with injects

---

## 📁 Structure

```
frontend-twin/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Home (redirects to login)
│   ├── login/page.tsx     # Login page
│   ├── layout.tsx         # Root layout
│   ├── globals.css        # Global styles
│   └── dashboard/         # Dashboard pages
│       ├── layout.tsx     # Dashboard layout with sidebar
│       ├── page.tsx       # AI Insights Dashboard
│       ├── bia/page.tsx   # Queue Theory BIA
│       └── scenarios/page.tsx # AI Scenario Generator
├── components/
│   ├── layout/
│   │   └── sidebar.tsx    # Navigation sidebar
│   ├── insights/
│   │   └── insight-card.tsx # AI Insight card
│   └── providers.tsx      # React Query provider
├── lib/
│   ├── api/
│   │   ├── client.ts      # Axios client
│   │   ├── types.ts       # TypeScript types
│   │   └── queries.ts     # React Query hooks
│   └── store/
│       └── auth.ts        # Zustand auth store
├── .env.local             # Environment variables
├── Dockerfile             # Docker build
├── next.config.js         # Next.js config
└── package.json           # Dependencies
```

---

## 🔌 API Integration

### Backend URL:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Endpoints Used:
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/organizations/`
- `GET /api/v1/organizations/{id}/insights` ⭐
- `POST /api/v1/bia/queue-theory` ⭐⭐⭐
- `GET /api/v1/scenarios/`
- `POST /api/v1/scenarios/ai-generate-advanced` ⭐⭐⭐

---

## 🐳 Docker

### Build:
```bash
docker build -t digital-twin-frontend .
```

### Run:
```bash
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 digital-twin-frontend
```

### Full Stack:
```bash
# From parent directory
docker-compose -f docker-compose.fullstack.yml up -d
```

---

## 🎯 TODO (optional)

- [ ] Personal Digital Twin page
- [ ] Simulations page
- [ ] Exercises page
- [ ] Predictions page
- [ ] Settings page
- [ ] Charts/graphs (recharts)
- [ ] Mobile responsive
- [ ] Dark mode
- [ ] Toast notifications

---

**Built with ❤️ for BCM professionals**
