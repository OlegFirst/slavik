# GitHub Pages Architecture - AI-Platform-ISO Documentation

**Version**: 1.0.0
**Date**: 2025-10-09
**Purpose**: Interactive Technical Documentation Website

---

## 1. Architecture Overview

### 1.1 Technology Stack

```
GitHub Pages (Jekyll/Static)
├── Frontend Framework: Next.js (Static Export) or Docusaurus
├── Styling: Tailwind CSS
├── Diagrams: Mermaid.js (interactive)
├── Search: Algolia DocSearch or Lunr.js
├── Analytics: Google Analytics / Plausible
└── Deployment: GitHub Actions
```

### 1.2 Site Structure

```
docs-website/
├── public/                  # Static assets
│   ├── diagrams/           # Mermaid diagram files
│   ├── images/             # Screenshots, logos
│   └── pdf/                # Downloadable PDFs
│
├── src/
│   ├── pages/              # Main pages
│   │   ├── index.tsx       # Home
│   │   ├── architecture/   # Architecture section
│   │   ├── services/       # Services catalog
│   │   ├── api/            # API reference
│   │   ├── diagrams/       # Interactive diagrams
│   │   └── library/        # Document library
│   │
│   ├── components/         # React components
│   │   ├── ServiceCard.tsx
│   │   ├── DiagramViewer.tsx
│   │   ├── DocumentSearch.tsx
│   │   └── Navigation.tsx
│   │
│   ├── data/               # Structured data
│   │   ├── services.json   # Service catalog
│   │   ├── diagrams.json   # Diagram metadata
│   │   └── documents.json  # Document index
│   │
│   └── styles/             # CSS
│
├── content/                # Markdown content
│   ├── architecture/       # Architecture docs
│   ├── guides/             # User guides
│   ├── api/                # API documentation
│   └── specs/              # Technical specs
│
├── scripts/                # Build scripts
│   ├── build-index.js      # Generate search index
│   ├── process-diagrams.js # Process Mermaid diagrams
│   └── generate-data.js    # Generate data files
│
└── .github/
    └── workflows/
        └── deploy.yml      # Deployment workflow
```

---

## 2. Core Features

### 2.1 Home Page

**URL**: `/`

**Sections**:
1. **Hero Section**
   - Platform overview
   - Key metrics (23 services, 11 AI modules, 347+ cases)
   - Quick start buttons

2. **Architecture Overview** (Interactive)
   - 4-layer diagram (clickable)
   - Hover: show details
   - Click: navigate to section

3. **Services Grid** (Interactive Cards)
   - 23 services
   - Status indicators (simulated)
   - Click: service details

4. **Quick Links**
   - API Reference
   - Deployment Guide
   - Specifications Catalog
   - Diagrams Library

5. **Latest Updates** (GitHub API)
   - Latest commits
   - Latest releases
   - Contributors

### 2.2 Architecture Section

**URL**: `/architecture`

**Sub-pages**:

#### `/architecture/overview`
- 4-layer architecture
- Interactive Mermaid diagram
- Click layers → drill down
- Component descriptions

#### `/architecture/services`
- Service dependency graph
- Interactive exploration
- Port mappings
- Technology stack per service

#### `/architecture/data-flow`
- Data flow diagrams
- EventBus topology
- Real-time event flows
- AI orchestration flow

#### `/architecture/infrastructure`
- Infrastructure components
- Database schema
- EventBus architecture
- Deployment architecture (Docker, K8s)

### 2.3 Services Catalog

**URL**: `/services`

**Features**:

#### Service Grid View
```typescript
interface Service {
  id: string;
  name: string;
  category: 'platform' | 'intelligent-core' | 'infrastructure';
  port: number;
  description: string;
  techStack: string[];
  dependencies: string[];
  apiEndpoints: number;
  documentation: string;
  repository: string;
  status: 'active' | 'development' | 'deprecated';
}
```

**Display**:
- Filterable by category
- Searchable
- Sortable (name, port, status)
- Card view with:
  - Service icon
  - Name & port
  - Tech stack badges
  - Quick actions (Docs, API, Code)

#### Service Detail Page `/services/{service-id}`

**Tabs**:
1. **Overview**
   - Description
   - Purpose
   - Key features
   - Metrics (if available)

2. **Architecture**
   - Component diagram
   - Dependencies (visual)
   - Data flow
   - Technology stack

3. **API Reference**
   - Endpoints list
   - Request/response examples
   - Authentication
   - Rate limits

4. **Integration**
   - How to integrate
   - Code examples
   - EventBus events
   - Dependencies

5. **Deployment**
   - Docker configuration
   - Environment variables
   - Health checks
   - Troubleshooting

### 2.4 Interactive Diagrams

**URL**: `/diagrams`

**Categories**:

#### Architecture Diagrams (24)
- Filterable by type
- Interactive Mermaid rendering
- Zoom & pan
- Export as PNG/SVG
- Full-screen mode

#### User Scenarios (4)
- BCM User Journey
- BIA Workflow
- Admin Monitoring
- Risk Assessment

#### Dependencies (1)
- Service Dependencies
- Interactive exploration
- Click service → show details

#### Flows (3)
- EventBus Message Flow
- Data Flow Complete
- AI Orchestration Flow

**Features**:
- **Live Rendering**: Mermaid.js
- **Interactive**: Click nodes → tooltips
- **Search**: Find diagrams by keyword
- **Collections**: Group related diagrams
- **Embed Code**: Copy embed code for external use

### 2.5 API Reference

**URL**: `/api`

**Structure**:

#### API Overview
- Base URL
- Authentication (JWT)
- Rate limits
- Error codes
- Versioning

#### By Service (grouped)
```
Platform Services (12 services)
├── BIA Service
│   ├── GET /api/bia
│   ├── POST /api/bia
│   └── [all endpoints]
├── Risk Service
│   └── [endpoints]
└── [other services]

Intelligent Core (11 modules)
└── [endpoints]

Infrastructure
└── [endpoints]
```

**Each Endpoint**:
- HTTP method + URL
- Description
- Parameters (query, body, headers)
- Request example (curl, JS, Python)
- Response example (JSON)
- Error responses
- Try it out (interactive)

**Tech**: OpenAPI 3.0 spec → Swagger UI / Redoc

### 2.6 Document Library

**URL**: `/library`

**Features**:

#### Main Library View
```
┌─────────────────────────────────────────────┐
│ Search: [___________________________] 🔍    │
├─────────────────────────────────────────────┤
│ Filters:                                     │
│ [ ] Specifications (108)                     │
│ [ ] Architecture (24)                        │
│ [ ] API Docs (3)                             │
│ [ ] Guides (15)                              │
│ [ ] Reports (24)                             │
├─────────────────────────────────────────────┤
│ Documents (550):                             │
│                                              │
│ 📄 TZ_USER_INTERFACE.md             35 KB   │
│    Technical specification for UI/UX         │
│    Tags: specification, ui, frontend         │
│    [View] [Download]                         │
│                                              │
│ 📄 TZ_AI_BCM_PLATFORM.md            63 KB   │
│    Main technical specification              │
│    [View] [Download]                         │
│                                              │
│ [... more documents ...]                     │
└─────────────────────────────────────────────┘
```

#### Document View `/library/{doc-id}`
- Rendered markdown
- Table of contents (auto-generated)
- Breadcrumbs
- Related documents
- Download options (MD, PDF)
- Edit on GitHub link
- Last updated info

#### Search Features
- Full-text search (Algolia or Lunr.js)
- Filters: category, file type, size, date
- Sorting: relevance, date, name, size
- Autocomplete
- Keyboard shortcuts (⌘K to search)

#### Collections
Pre-defined collections:
- **Getting Started** (5 docs)
- **Technical Specifications** (108 docs)
- **API Documentation** (3 docs)
- **Deployment Guides** (10 docs)
- **Architecture Docs** (24 docs)

---

## 3. Data Structure

### 3.1 Services Data (`services.json`)

```json
{
  "services": [
    {
      "id": "bia-service",
      "name": "BIA Service",
      "category": "platform-services",
      "port": 8012,
      "description": "Business Impact Analysis service with 6-step wizard",
      "version": "2.0.0",
      "techStack": ["Python 3.11", "FastAPI", "PostgreSQL", "Redis"],
      "dependencies": ["ai-foundation", "workflow-intelligence", "eventbus"],
      "apiEndpoints": 15,
      "documentation": "/docs/platform-services/bia-service/",
      "repository": "platform-services/bia-service",
      "healthCheck": "http://localhost:8012/health",
      "status": "active",
      "features": [
        "6-step BIA wizard",
        "AI-assisted analysis",
        "Dependency mapping",
        "RTO/RPO recommendations"
      ],
      "events": {
        "publishes": ["BIA.Started", "BIA.Completed", "BIA.FunctionsAnalyzed"],
        "subscribes": ["User.Action"]
      }
    }
    // ... 22 more services
  ]
}
```

### 3.2 Diagrams Data (`diagrams.json`)

```json
{
  "diagrams": [
    {
      "id": "platform-architecture",
      "title": "Platform Architecture Overview",
      "category": "architecture",
      "file": "architecture/platform-architecture.mmd",
      "description": "4-layer platform architecture",
      "tags": ["architecture", "overview", "layers"],
      "lastUpdated": "2025-10-09",
      "complexity": "high",
      "relatedDiagrams": ["service-dependencies", "data-flow"],
      "relatedDocs": ["ARCHITECTURE.md", "DEPLOYMENT_GUIDE.md"]
    }
    // ... 35 more diagrams
  ]
}
```

### 3.3 Documents Index (`documents.json`)

```json
{
  "documents": [
    {
      "id": "tz-user-interface",
      "title": "Technical Specification: User Interface & Administrator Panel",
      "path": "doc-project/TZ_USER_INTERFACE.md",
      "category": "specification",
      "type": "technical-specification",
      "size": 35840,
      "tags": ["ui", "ux", "frontend", "specification"],
      "description": "Complete web-based user interface with administrator panel",
      "lastUpdated": "2025-10-09",
      "author": "Claude Code",
      "relatedDocs": ["TZ_AI_BCM_PLATFORM.md", "ARCHITECTURE.md"],
      "sections": [
        "Executive Summary",
        "Technical Stack",
        "User Interface Structure",
        "Administrator Panel",
        "Timeline & Phases"
      ]
    }
    // ... 549 more documents
  ]
}
```

---

## 4. Implementation Details

### 4.1 Technology Choice: Docusaurus vs Next.js

**Recommended: Docusaurus 3.0**

**Pros**:
- ✅ Built for documentation
- ✅ Markdown-first
- ✅ Built-in search (Algolia)
- ✅ Versioning support
- ✅ i18n support
- ✅ Fast static site generation
- ✅ React components in MDX
- ✅ Plugin ecosystem

**Next.js Alternative**:
- More flexibility
- Better for custom features
- Requires more setup

**Decision**: Use **Docusaurus** for faster development with documentation focus.

### 4.2 Directory Structure (Docusaurus)

```
docs-website/
├── docs/                   # Documentation content
│   ├── architecture/
│   ├── services/
│   ├── api/
│   └── guides/
│
├── src/
│   ├── components/
│   │   ├── ServiceCard.tsx
│   │   ├── DiagramViewer.tsx
│   │   ├── InteractiveDiagram.tsx
│   │   └── DocumentSearch.tsx
│   │
│   ├── pages/              # Custom pages
│   │   ├── index.tsx       # Home
│   │   ├── services.tsx    # Services catalog
│   │   └── diagrams.tsx    # Diagram gallery
│   │
│   ├── css/
│   │   └── custom.css
│   │
│   └── data/
│       ├── services.ts
│       ├── diagrams.ts
│       └── documents.ts
│
├── static/
│   ├── diagrams/           # .mmd files
│   ├── img/
│   └── pdf/
│
├── docusaurus.config.js
├── sidebars.js
└── package.json
```

### 4.3 Key Components

#### 4.3.1 ServiceCard Component

```typescript
// src/components/ServiceCard.tsx
import React from 'react';

interface ServiceCardProps {
  service: Service;
}

export const ServiceCard: React.FC<ServiceCardProps> = ({ service }) => {
  return (
    <div className="service-card">
      <div className="service-header">
        <h3>{service.name}</h3>
        <span className="port-badge">:{service.port}</span>
        <span className={`status-badge ${service.status}`}>
          {service.status}
        </span>
      </div>

      <p className="description">{service.description}</p>

      <div className="tech-stack">
        {service.techStack.map(tech => (
          <span key={tech} className="tech-badge">{tech}</span>
        ))}
      </div>

      <div className="actions">
        <a href={`/services/${service.id}`}>Details</a>
        <a href={`/api#${service.id}`}>API</a>
        <a href={service.repository}>Code</a>
      </div>
    </div>
  );
};
```

#### 4.3.2 Interactive Diagram Viewer

```typescript
// src/components/DiagramViewer.tsx
import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

interface DiagramViewerProps {
  diagram: string; // Mermaid code
  title: string;
  interactive?: boolean;
}

export const DiagramViewer: React.FC<DiagramViewerProps> = ({
  diagram,
  title,
  interactive = true
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
    });

    if (containerRef.current) {
      mermaid.render('diagram', diagram).then(({ svg }) => {
        containerRef.current!.innerHTML = svg;

        if (interactive) {
          addInteractivity();
        }
      });
    }
  }, [diagram, interactive]);

  const addInteractivity = () => {
    // Add click handlers to nodes
    const nodes = containerRef.current?.querySelectorAll('.node');
    nodes?.forEach(node => {
      node.addEventListener('click', (e) => {
        const nodeId = node.getAttribute('id');
        showNodeDetails(nodeId);
      });
    });
  };

  const showNodeDetails = (nodeId: string) => {
    // Show tooltip or modal with node details
    console.log('Node clicked:', nodeId);
  };

  return (
    <div className="diagram-viewer">
      <h3>{title}</h3>
      <div
        ref={containerRef}
        className="diagram-container"
      />
      <div className="diagram-actions">
        <button onClick={() => exportAsPNG()}>Export PNG</button>
        <button onClick={() => exportAsSVG()}>Export SVG</button>
        <button onClick={() => toggleFullscreen()}>Fullscreen</button>
      </div>
    </div>
  );
};
```

#### 4.3.3 Document Search Component

```typescript
// src/components/DocumentSearch.tsx
import React, { useState } from 'react';
import { DocSearch } from '@docsearch/react';
import '@docsearch/css';

export const DocumentSearch: React.FC = () => {
  const [query, setQuery] = useState('');

  return (
    <div className="document-search">
      <DocSearch
        apiKey="YOUR_ALGOLIA_API_KEY"
        indexName="ai-platform-iso"
        appId="YOUR_APP_ID"
      />
    </div>
  );
};
```

### 4.4 Data Generation Scripts

#### Generate Services Data

```javascript
// scripts/generate-services-data.js
const fs = require('fs');
const path = require('path');
const yaml = require('yaml');

// Read service catalog from existing YAML
const catalogPath = path.join(__dirname, '../docs-old-backup/architecture/SERVICE_CATALOG.yaml');
const catalog = yaml.parse(fs.readFileSync(catalogPath, 'utf8'));

// Transform to JSON for website
const services = {
  services: Object.entries(catalog.services).map(([id, service]) => ({
    id: id,
    name: service.name,
    category: determineCategory(id),
    port: service.port,
    description: service.description,
    techStack: service.tech_stack || [],
    dependencies: service.depends_on || [],
    apiEndpoints: service.endpoints?.length || 0,
    documentation: `/docs/services/${id}`,
    repository: `https://github.com/yourorg/ai-platform-iso/tree/main/${getServicePath(id)}`,
    status: 'active',
    features: service.capabilities || []
  }))
};

fs.writeFileSync(
  path.join(__dirname, '../src/data/services.json'),
  JSON.stringify(services, null, 2)
);

console.log(`✅ Generated services data: ${services.services.length} services`);
```

#### Generate Document Index

```javascript
// scripts/generate-document-index.js
const fs = require('fs');
const path = require('path');
const glob = require('glob');
const matter = require('gray-matter');

const rootDir = path.join(__dirname, '..');
const docsDir = path.join(rootDir, 'docs');
const projectDir = path.join(rootDir, 'doc-project');

const documents = [];

// Scan all markdown files
const files = [
  ...glob.sync(`${docsDir}/**/*.md`),
  ...glob.sync(`${projectDir}/**/*.md`)
];

files.forEach(filePath => {
  const content = fs.readFileSync(filePath, 'utf8');
  const { data: frontmatter, content: body } = matter(content);
  const stats = fs.statSync(filePath);

  const relativePath = path.relative(rootDir, filePath);
  const id = relativePath.replace(/\//g, '-').replace('.md', '');

  documents.push({
    id,
    title: frontmatter.title || extractTitle(body),
    path: relativePath,
    category: determineCategory(relativePath),
    type: determineType(relativePath),
    size: stats.size,
    tags: frontmatter.tags || extractTags(body),
    description: frontmatter.description || extractDescription(body),
    lastUpdated: stats.mtime.toISOString().split('T')[0],
    sections: extractSections(body)
  });
});

const index = {
  documents,
  totalCount: documents.length,
  categories: getCategoryCounts(documents),
  lastGenerated: new Date().toISOString()
};

fs.writeFileSync(
  path.join(rootDir, 'src/data/documents.json'),
  JSON.stringify(index, null, 2)
);

console.log(`✅ Generated document index: ${documents.length} documents`);
```

---

## 5. Deployment

### 5.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: docs-website/package-lock.json

      - name: Install dependencies
        working-directory: ./docs-website
        run: npm ci

      - name: Generate data files
        working-directory: ./docs-website
        run: |
          node scripts/generate-services-data.js
          node scripts/generate-diagrams-data.js
          node scripts/generate-document-index.js

      - name: Build website
        working-directory: ./docs-website
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: docs-website/build

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

### 5.2 Configuration

```javascript
// docusaurus.config.js
module.exports = {
  title: 'AI-Platform-ISO',
  tagline: 'Business Continuity Management Platform with AI',
  url: 'https://yourorg.github.io',
  baseUrl: '/ai-platform-iso/',
  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'yourorg',
  projectName: 'ai-platform-iso',

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/yourorg/ai-platform-iso/edit/main/docs-website/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'AI-Platform-ISO',
      logo: {
        alt: 'Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/services',
          label: 'Services',
          position: 'left',
        },
        {
          to: '/diagrams',
          label: 'Diagrams',
          position: 'left',
        },
        {
          to: '/api',
          label: 'API',
          position: 'left',
        },
        {
          to: '/library',
          label: 'Library',
          position: 'left',
        },
        {
          href: 'https://github.com/yourorg/ai-platform-iso',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            { label: 'Getting Started', to: '/docs/intro' },
            { label: 'Architecture', to: '/docs/architecture' },
            { label: 'API Reference', to: '/api' },
          ],
        },
        {
          title: 'Resources',
          items: [
            { label: 'Services Catalog', to: '/services' },
            { label: 'Diagrams', to: '/diagrams' },
            { label: 'Document Library', to: '/library' },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} AI-Platform-ISO`,
    },
    prism: {
      theme: require('prism-react-renderer/themes/github'),
      darkTheme: require('prism-react-renderer/themes/dracula'),
    },
    algolia: {
      apiKey: 'YOUR_API_KEY',
      indexName: 'ai-platform-iso',
      appId: 'YOUR_APP_ID',
    },
  },

  plugins: [
    [
      require.resolve('@docusaurus/plugin-content-docs'),
      {
        id: 'architecture',
        path: 'architecture',
        routeBasePath: 'architecture',
        sidebarPath: require.resolve('./sidebarsArchitecture.js'),
      },
    ],
  ],
};
```

---

## 6. Features Roadmap

### Phase 1: Core (Week 1-2)
- ✅ Setup Docusaurus
- ✅ Home page with hero
- ✅ Services catalog page
- ✅ Basic documentation pages
- ✅ Deploy to GitHub Pages

### Phase 2: Interactive (Week 3-4)
- ✅ Interactive Mermaid diagrams
- ✅ Service detail pages
- ✅ Document search (Algolia)
- ✅ Diagram viewer with zoom

### Phase 3: Advanced (Week 5-6)
- ✅ API reference (Swagger UI)
- ✅ Document library with filters
- ✅ Related documents suggestions
- ✅ GitHub integration (latest commits, contributors)

### Phase 4: Polish (Week 7-8)
- ✅ Dark mode
- ✅ Performance optimization
- ✅ SEO optimization
- ✅ Analytics integration

---

## 7. Metrics & Analytics

### 7.1 Key Metrics

- Page views
- Most visited pages
- Search queries
- Document downloads
- Diagram views
- API endpoint documentation views

### 7.2 Tools

- **Google Analytics** or **Plausible** (privacy-friendly)
- **Hotjar** (heatmaps, recordings)
- **GitHub Insights** (traffic, clones)

---

**Status**: Architecture Complete
**Next**: Implementation
**Timeline**: 8 weeks
