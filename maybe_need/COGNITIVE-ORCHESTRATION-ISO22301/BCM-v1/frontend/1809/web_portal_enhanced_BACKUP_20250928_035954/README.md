# BCM Web Portal v2

A modern, comprehensive Business Continuity Management (BCM) platform built with Vue 3, TypeScript, and Vite. This application provides enterprise-grade BCM capabilities including risk assessment, business impact analysis, crisis management, and AI-powered insights.

## 🚀 Features

### Core BCM Modules
- **Risk Assessment** - Comprehensive risk identification and evaluation
- **Business Impact Analysis** - Detailed business process impact assessment
- **BCP Development** - Business continuity plan creation and management
- **Crisis Management** - Real-time crisis response coordination
- **Incident Management** - Incident tracking and resolution workflows
- **Emergency Response** - Emergency procedures and contact management
- **Disaster Recovery** - IT and operational recovery planning
- **Compliance Management** - ISO 22301 and regulatory compliance tracking

### Advanced Features
- **AI Assistant** - Intelligent BCM guidance and content generation
- **Real-time Dashboards** - Executive and operational dashboards
- **Document Management** - Centralized BCM document repository
- **Training Management** - Staff training and certification tracking
- **Audit Management** - Internal and external audit coordination
- **Performance Metrics** - KPI tracking and reporting
- **Multi-language Support** - Internationalization ready

### Technical Features
- **Modern Vue 3** with Composition API and TypeScript
- **Professional UI** with Anthropic-inspired design system
- **Responsive Design** - Mobile-first approach
- **PWA Ready** - Progressive Web App capabilities
- **Dark Mode** - Full dark theme support
- **Security First** - Comprehensive security headers and CSP
- **Docker Ready** - Production-ready containerization

## 🛠 Technology Stack

- **Frontend Framework**: Vue 3 with Composition API
- **Build Tool**: Vite
- **Language**: TypeScript
- **State Management**: Pinia
- **Routing**: Vue Router 4
- **Styling**: SCSS + Tailwind CSS utilities
- **Icons**: Heroicons
- **HTTP Client**: Axios
- **Notifications**: Vue Toastification
- **Charts**: Chart.js + Vue-ChartJS
- **Testing**: Vitest + Vue Test Utils
- **Deployment**: Docker + Nginx

## 📋 Prerequisites

- Node.js 18.0 or higher
- npm 9.0 or higher
- Docker (for containerized deployment)

## 🚦 Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bcm-web-portal-v2
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual container
docker build -t bcm-web-portal-v2 .
docker run -p 3000:80 bcm-web-portal-v2
```

## 📁 Project Structure

```
web_portal_v2/
├── public/                 # Static assets
│   ├── manifest.json      # PWA manifest
│   ├── robots.txt         # SEO robots file
│   └── logo.svg           # Application logo
├── src/
│   ├── components/        # Reusable Vue components
│   │   ├── layout/        # Layout components (Header, Sidebar, Footer)
│   │   ├── ui/            # UI components (Button, Card, etc.)
│   │   └── modules/       # BCM module-specific components
│   ├── views/             # Page components
│   │   └── modules/       # BCM module views (20+ modules)
│   ├── stores/            # Pinia store modules
│   ├── services/          # API service layers
│   ├── router/            # Vue Router configuration
│   ├── styles/            # SCSS stylesheets and design system
│   ├── utils/             # Utility functions and helpers
│   ├── types/             # TypeScript type definitions
│   ├── App.vue            # Root Vue component
│   └── main.ts            # Application entry point
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile            # Docker build configuration
├── nginx.conf            # Nginx configuration
├── vite.config.ts        # Vite build configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Project dependencies and scripts
```

## 🔧 Available Scripts

```bash
# Development
npm run dev              # Start development server
npm run build           # Build for production
npm run preview         # Preview production build

# Code Quality
npm run type-check      # TypeScript type checking
npm run lint            # ESLint linting
npm run format          # Prettier code formatting

# Testing
npm run test            # Run unit tests
npm run test:ui         # Run tests with UI
npm run coverage        # Generate test coverage report
```

## 🌐 Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_VERSION=v1

# Application Settings
VITE_APP_TITLE="BCM Platform v2"
VITE_APP_ENV=production

# Feature Flags
VITE_ENABLE_AI_ASSISTANT=true
VITE_ENABLE_NOTIFICATIONS=true
VITE_ENABLE_DEBUG_MODE=false
```

## 🎨 Design System

The application uses a comprehensive design system inspired by Anthropic's design principles:

- **Colors**: Professional blue palette with semantic colors
- **Typography**: Modern font stack with clear hierarchy
- **Components**: Consistent, accessible UI components
- **Spacing**: 8px grid system for consistent layouts
- **Responsive**: Mobile-first responsive design

## 🔐 Security Features

- Content Security Policy (CSP) headers
- XSS protection headers
- CSRF protection
- Secure authentication with JWT
- Rate limiting and DDoS protection
- Input validation and sanitization
- Secure Docker configuration

## 🚀 Deployment

### Docker Deployment (Recommended)

1. **Configure environment variables**
2. **Build and deploy with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

### Manual Deployment

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Configure web server** (Nginx, Apache, etc.) to serve the `dist` folder

3. **Set up reverse proxy** for API calls

## 🧪 Testing

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run coverage

# Run tests with UI
npm run test:ui
```

## 📈 Performance

- **Lighthouse Score**: 90+ across all metrics
- **Bundle Size**: Optimized with code splitting
- **Caching**: Aggressive caching for static assets
- **CDN Ready**: Optimized for CDN deployment
- **Lazy Loading**: Route-based code splitting

## 🌍 Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Mobile

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.bcm.example.com](https://docs.bcm.example.com)
- **Support Portal**: [support.bcm.example.com](https://support.bcm.example.com)
- **Issues**: Create an issue in this repository

## 🗺 Roadmap

- [ ] Advanced AI analytics and predictions
- [ ] Real-time collaboration features
- [ ] Mobile native applications
- [ ] Advanced workflow automation
- [ ] Third-party integrations (SIEM, ITSM)
- [ ] Advanced reporting and dashboards

---

**Built with ❤️ by the BCM Platform Team**