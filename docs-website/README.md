# AI-Platform-ISO Documentation Website

**Status**: 🚧 Ready for Implementation
**Technology**: Docusaurus 3.0 + React + TypeScript
**Deployment**: GitHub Pages
**Timeline**: 8 weeks

---

## 🎯 Overview

Interactive technical documentation website for AI-Platform-ISO platform showcasing:

- **23 Services** with detailed specifications
- **36 Interactive Diagrams** (Mermaid.js)
- **550+ Documents** with full-text search
- **108 Technical Specifications**
- **Complete API Reference** (150+ endpoints)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Pages                          │
│              (Static Site Hosting)                       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Docusaurus Frontend                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   React      │  │  Mermaid.js  │  │  Algolia     │  │
│  │  Components  │  │  (Diagrams)  │  │  (Search)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Static Data Files                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ services.json│  │diagrams.json │  │documents.json│  │
│  │  (23 items)  │  │  (36 items)  │  │ (550 items)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
docs-website/
├── 📄 README.md                    # This file
├── 📄 ARCHITECTURE.md              # Detailed architecture
├── 📄 IMPLEMENTATION_GUIDE.md      # Step-by-step implementation
│
├── 📦 src/
│   ├── components/                 # React components
│   │   ├── ServiceCard/           # Service display card
│   │   ├── DiagramViewer/         # Interactive diagram viewer
│   │   └── DocumentSearch/        # Document search component
│   │
│   ├── pages/                      # Custom pages
│   │   ├── index.tsx              # Home page
│   │   ├── services.tsx           # Services catalog
│   │   ├── diagrams.tsx           # Diagram gallery
│   │   └── library.tsx            # Document library
│   │
│   ├── data/                       # Generated data files
│   │   ├── services.json          # 23 services
│   │   ├── diagrams.json          # 36 diagrams
│   │   └── documents.json         # 550 documents
│   │
│   └── css/
│       └── custom.css             # Custom styling
│
├── 📚 docs/                        # Markdown documentation
│   ├── intro.md
│   ├── architecture/
│   ├── services/
│   ├── api/
│   └── guides/
│
├── 🎨 static/                      # Static assets
│   ├── diagrams/                  # Mermaid .mmd files (36)
│   ├── img/
│   └── pdf/
│
├── 🔧 scripts/                     # Data generation scripts
│   ├── generate-all-data.js
│   ├── generate-services-data.js
│   ├── generate-diagrams-data.js
│   └── generate-document-index.js
│
├── ⚙️ .github/
│   └── workflows/
│       └── deploy.yml             # GitHub Actions deployment
│
├── 📋 package.json
├── 📋 tsconfig.json
└── 📋 docusaurus.config.ts
```

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# 1. Initialize Docusaurus
cd docs-website
npx create-docusaurus@latest . classic --typescript

# 2. Install dependencies
npm install

# 3. Install additional packages
npm install --save \
  mermaid \
  @docsearch/react \
  gray-matter \
  glob \
  yaml \
  react-icons \
  clsx

# 4. Generate data files
npm run generate-data

# 5. Start development server
npm start
```

Open http://localhost:3000

---

## 📊 Features

### 1. Services Catalog (`/services`)

**Display**:
- Grid view of all 23 services
- Filters: Platform Services (12), Intelligent Core (11)
- Search by name, description
- Service cards showing:
  - Name & port
  - Status (Active, Development)
  - Tech stack
  - API endpoint count
  - Quick links (Details, API, Code)

**Service Detail Pages**:
- Overview & description
- Architecture diagram
- API endpoints list
- Technology stack
- Dependencies
- Integration guide
- Deployment instructions

### 2. Interactive Diagrams (`/diagrams`)

**36 Mermaid Diagrams**:
- **Architecture** (24): Platform overview, service dependencies, data flow
- **User Scenarios** (4): BCM journey, BIA workflow, admin monitoring, risk assessment
- **Dependencies** (1): Detailed service dependency graph
- **Flows** (3): EventBus flow, data flow, AI orchestration
- **Integration** (4): Integration patterns
- **Business Processes** (1): Document generation

**Features**:
- Live Mermaid.js rendering
- Interactive exploration (click nodes → details)
- Zoom & pan
- Export as PNG/SVG
- Full-screen mode
- Search diagrams
- Filter by category

### 3. Document Library (`/library`)

**550+ Documents**:
- Full-text search (Algolia DocSearch)
- Filters:
  - Category (Specification, Architecture, Guide, Report)
  - File type (MD, PDF)
  - Size, Date
- Sort: Relevance, Date, Name, Size
- Collections:
  - Getting Started (5 docs)
  - Technical Specifications (108 docs)
  - API Documentation (3 docs)
  - Deployment Guides (10 docs)

**Document View**:
- Rendered Markdown
- Auto-generated TOC
- Breadcrumbs
- Related documents
- Download options
- Edit on GitHub link

### 4. API Reference (`/api`)

**150+ Endpoints**:
- Grouped by service
- Interactive Swagger UI
- Request/response examples
- Authentication guide
- Try it out feature
- Code examples (curl, JavaScript, Python)

### 5. Architecture Section (`/architecture`)

**Sub-sections**:
- Overview: 4-layer architecture
- Services: Service dependency graph
- Data Flow: EventBus, AI orchestration
- Infrastructure: Deployment architecture (Docker, K8s)
- All with interactive diagrams

---

## 🎨 Customization

### Branding

Edit `docusaurus.config.ts`:

```typescript
{
  title: 'Your Platform Name',
  tagline: 'Your Tagline',
  favicon: 'img/favicon.ico',
  url: 'https://yourorg.github.io',
  baseUrl: '/your-repo/',
  organizationName: 'yourorg',
  projectName: 'your-repo',
}
```

### Styling

Edit `src/css/custom.css`:

```css
:root {
  --ifm-color-primary: #2e8555;
  --ifm-color-primary-dark: #29784c;
  /* ... */
}
```

### Navigation

Edit `docusaurus.config.ts` → `themeConfig.navbar.items`

---

## 📦 Data Generation

### Services Data

```bash
node scripts/generate-services-data.js
# Output: src/data/services.json (23 services)
```

Contains:
- Service ID, name, port
- Description
- Tech stack
- Dependencies
- API endpoint count
- Status (active, development)
- Features list

### Diagrams Data

```bash
node scripts/generate-diagrams-data.js
# Output: src/data/diagrams.json (36 diagrams)
```

Scans `/doc-project/diagrams/` and extracts:
- Diagram metadata
- Category, type
- File path
- Last updated date

### Document Index

```bash
node scripts/generate-document-index.js
# Output: src/data/documents.json (550 documents)
```

Scans all `.md` files in `/docs/` and `/doc-project/`:
- Title, description
- File path, size
- Category, type
- Tags
- Sections (extracted from headings)

### Generate All

```bash
npm run generate-data
# Runs all three scripts
```

---

## 🚢 Deployment

### GitHub Actions (Automatic)

Push to `main` branch triggers deployment:

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - uses: actions/deploy-pages@v2
```

### Manual Deployment

```bash
npm run build
npm run deploy
```

### Custom Domain

Add `static/CNAME` file:

```
docs.yourplatform.com
```

Configure DNS:
```
CNAME record: docs → yourorg.github.io
```

---

## 🔍 Search Integration

### Algolia DocSearch

1. Apply at https://docsearch.algolia.com/apply/
2. Get API keys
3. Update `docusaurus.config.ts`:

```typescript
algolia: {
  appId: 'YOUR_APP_ID',
  apiKey: 'YOUR_API_KEY',
  indexName: 'ai-platform-iso',
}
```

### Alternative: Local Search (Lunr.js)

Install plugin:

```bash
npm install --save @easyops-cn/docusaurus-search-local
```

---

## 📈 Analytics

### Google Analytics

```typescript
// docusaurus.config.ts
gtag: {
  trackingID: 'G-XXXXXXXXXX',
}
```

### Plausible (Privacy-friendly)

```typescript
scripts: [
  {
    src: 'https://plausible.io/js/script.js',
    defer: true,
    'data-domain': 'yourorg.github.io',
  },
],
```

---

## 🧪 Testing

```bash
# Build
npm run build

# Serve locally
npm run serve
# Open http://localhost:3000

# Check for broken links
npm run build && npx broken-link-checker http://localhost:3000
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Detailed architecture design |
| [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) | Step-by-step implementation guide |
| [README.md](README.md) | This file - Quick start & overview |

---

## 🗓️ Timeline

| Week | Milestone |
|------|-----------|
| 1 | Setup, basic structure, generate data |
| 2 | Service catalog, search |
| 3 | Diagram viewer (Mermaid) |
| 4 | Document library |
| 5 | API reference (Swagger UI) |
| 6 | Interactive features, polish |
| 7 | Testing, optimization |
| 8 | Documentation, deployment, launch |

**Total**: 8 weeks (1 developer)

---

## 🎯 Success Metrics

- **Pages**: 100+ pages
- **Services**: 23 cataloged
- **Diagrams**: 36 interactive
- **Documents**: 550+ indexed
- **API Endpoints**: 150+ documented
- **Search**: Full-text with autocomplete
- **Performance**: Lighthouse score > 90
- **Mobile**: Fully responsive

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## 📝 License

See [LICENSE](../LICENSE)

---

## 🔗 Links

- **Live Site**: https://yourorg.github.io/ai-platform-iso/
- **GitHub Repository**: https://github.com/yourorg/ai-platform-iso
- **Docusaurus**: https://docusaurus.io/
- **Mermaid.js**: https://mermaid.js.org/

---

**Status**: ✅ Architecture Complete, Ready for Implementation
**Next Steps**: Run `npx create-docusaurus@latest . classic --typescript`
