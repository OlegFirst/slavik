# Implementation Guide - GitHub Pages Documentation Website

**Version**: 1.0.0
**Date**: 2025-10-09
**Estimated Time**: 8 weeks

---

## Quick Start

```bash
# 1. Navigate to docs-website directory
cd /Users/MD/AI-Platform-ISO/docs-website

# 2. Initialize Docusaurus
npx create-docusaurus@latest . classic --typescript

# 3. Install additional dependencies
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

---

## File-by-File Implementation

### 1. Package Configuration

#### `package.json`

```json
{
  "name": "ai-platform-iso-docs",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "docusaurus": "docusaurus",
    "start": "docusaurus start",
    "build": "npm run generate-data && docusaurus build",
    "swizzle": "docusaurus swizzle",
    "deploy": "docusaurus deploy",
    "clear": "docusaurus clear",
    "serve": "docusaurus serve",
    "write-translations": "docusaurus write-translations",
    "write-heading-ids": "docusaurus write-heading-ids",
    "generate-data": "node scripts/generate-all-data.js"
  },
  "dependencies": {
    "@docusaurus/core": "^3.0.0",
    "@docusaurus/preset-classic": "^3.0.0",
    "@docusaurus/theme-mermaid": "^3.0.0",
    "@docsearch/react": "^3.5.2",
    "@mdx-js/react": "^3.0.0",
    "clsx": "^2.0.0",
    "gray-matter": "^4.0.3",
    "mermaid": "^10.6.1",
    "prism-react-renderer": "^2.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-icons": "^4.12.0"
  },
  "devDependencies": {
    "@docusaurus/module-type-aliases": "^3.0.0",
    "@docusaurus/types": "^3.0.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "glob": "^10.3.10",
    "typescript": "~5.2.0",
    "yaml": "^2.3.4"
  },
  "browserslist": {
    "production": [
      ">0.5%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "engines": {
    "node": ">=18.0"
  }
}
```

---

### 2. Docusaurus Configuration

#### `docusaurus.config.ts`

```typescript
import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'AI-Platform-ISO',
  tagline: 'Business Continuity Management Platform with AI Intelligence',
  favicon: 'img/favicon.ico',

  url: 'https://yourorg.github.io',
  baseUrl: '/ai-platform-iso/',

  organizationName: 'yourorg',
  projectName: 'ai-platform-iso',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/yourorg/ai-platform-iso/tree/main/docs-website/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  markdown: {
    mermaid: true,
  },

  themes: ['@docusaurus/theme-mermaid'],

  themeConfig: {
    image: 'img/social-card.jpg',
    navbar: {
      title: 'AI-Platform-ISO',
      logo: {
        alt: 'AI-Platform-ISO Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Documentation',
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
          label: 'API Reference',
          position: 'left',
        },
        {
          to: '/library',
          label: 'Document Library',
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
            {
              label: 'Getting Started',
              to: '/docs/intro',
            },
            {
              label: 'Architecture',
              to: '/docs/architecture/overview',
            },
            {
              label: 'API Reference',
              to: '/api',
            },
            {
              label: 'Deployment Guide',
              to: '/docs/deployment',
            },
          ],
        },
        {
          title: 'Platform',
          items: [
            {
              label: 'Services Catalog (23)',
              to: '/services',
            },
            {
              label: 'Diagrams (36)',
              to: '/diagrams',
            },
            {
              label: 'Specifications (108)',
              to: '/library?filter=specification',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'Document Library (550+)',
              to: '/library',
            },
            {
              label: 'GitHub Repository',
              href: 'https://github.com/yourorg/ai-platform-iso',
            },
            {
              label: 'ISO 22301 Compliance',
              to: '/docs/compliance/iso-22301',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} AI-Platform-ISO. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'json', 'yaml', 'python', 'typescript'],
    },
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'ai-platform-iso',
      contextualSearch: true,
      searchPagePath: 'search',
    },
    mermaid: {
      theme: {light: 'default', dark: 'dark'},
      options: {
        maxTextSize: 50000,
      },
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
```

---

### 3. Data Generation Scripts

#### `scripts/generate-all-data.js`

```javascript
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🚀 Generating all data files...\n');

// Run all generation scripts
const scripts = [
  './generate-services-data.js',
  './generate-diagrams-data.js',
  './generate-document-index.js',
];

scripts.forEach(script => {
  console.log(`Running: ${script}`);
  require(script);
  console.log('');
});

console.log('✅ All data files generated successfully!');
```

#### `scripts/generate-services-data.js`

```javascript
const fs = require('fs');
const path = require('path');

// Hardcoded services data based on your platform
const services = {
  "platform-services": [
    {
      id: "bia-service",
      name: "BIA Service",
      port: 8012,
      description: "Business Impact Analysis service with 6-step wizard, AI-assisted analysis",
      techStack: ["Python 3.11", "FastAPI", "PostgreSQL", "Redis"],
      dependencies: ["ai-foundation", "workflow-intelligence", "eventbus"],
      apiEndpoints: 15,
      status: "active",
      features: ["6-step wizard", "AI analysis", "Dependency mapping", "RTO/RPO recommendations"]
    },
    {
      id: "risk-service",
      name: "Risk Service",
      port: 8040,
      description: "Risk assessment and management with AI recommendations",
      techStack: ["Python 3.11", "FastAPI", "PostgreSQL"],
      dependencies: ["ai-foundation", "expertise-center"],
      apiEndpoints: 12,
      status: "active",
      features: ["Risk register", "Heat map", "AI mitigation", "Treatment plans"]
    },
    {
      id: "compliance-service",
      name: "Compliance Service",
      port: 8014,
      description: "ISO 22301 compliance tracking and gap analysis",
      techStack: ["Python 3.11", "FastAPI", "PostgreSQL"],
      dependencies: ["ai-foundation"],
      apiEndpoints: 10,
      status: "active",
      features: ["ISO 22301 tracking", "Gap analysis", "Evidence management", "Audit trail"]
    },
    {
      id: "governance-service",
      name: "Governance Service",
      port: 8013,
      description: "BCM governance and policy management",
      techStack: ["Python 3.11", "FastAPI", "PostgreSQL"],
      dependencies: [],
      apiEndpoints: 8,
      status: "active",
      features: ["Policy management", "Governance framework", "Reporting"]
    },
    {
      id: "planning-service",
      name: "Planning Service",
      port: 8011,
      description: "BC plan creation and management",
      techStack: ["Python 3.11", "FastAPI", "PostgreSQL"],
      dependencies: ["workflow-intelligence", "ai-foundation"],
      apiEndpoints: 14,
      status: "active",
      features: ["Plan wizard", "Templates", "AI generation", "Version control"]
    },
    {
      id: "plans-service",
      name: "Plans Service",
      port: 8023,
      description: "BC plan storage and retrieval",
      techStack: ["Python 3.11", "FastAPI", "PostgreSQL"],
      dependencies: [],
      apiEndpoints: 8,
      status: "active",
      features: ["Plan library", "Search", "Export"]
    },
    {
      id: "response-service",
      name: "Response Service",
      port: 8041,
      description: "Incident response coordination",
      techStack: ["Python 3.11", "FastAPI", "PostgreSQL", "RabbitMQ"],
      dependencies: ["eventbus"],
      apiEndpoints: 10,
      status: "active",
      features: ["Incident management", "Real-time coordination", "Escalation"]
    },
    {
      id: "documents-service",
      name: "Documents Service",
      port: 8024,
      description: "Document management and versioning",
      techStack: ["Python 3.11", "FastAPI", "PostgreSQL", "S3"],
      dependencies: [],
      apiEndpoints: 12,
      status: "active",
      features: ["Document storage", "Versioning", "Search", "Templates"]
    },
    {
      id: "validation-service",
      name: "Validation Service",
      port: 8022,
      description: "Data validation and quality checks",
      techStack: ["Python 3.11", "FastAPI"],
      dependencies: [],
      apiEndpoints: 6,
      status: "active",
      features: ["Schema validation", "Quality checks", "Error reporting"]
    },
    {
      id: "learning-service",
      name: "Learning Service",
      port: 8021,
      description: "Training and knowledge management",
      techStack: ["Python 3.11", "FastAPI", "PostgreSQL"],
      dependencies: ["collective"],
      apiEndpoints: 15,
      status: "active",
      features: ["Training modules", "Case studies", "Certifications", "Progress tracking"]
    },
    {
      id: "community-service",
      name: "Community Service",
      port: 8030,
      description: "Community portal and peer learning",
      techStack: ["Python 3.11", "FastAPI", "PostgreSQL"],
      dependencies: ["community-intelligence"],
      apiEndpoints: 18,
      status: "active",
      features: ["Forums", "Q&A", "Best practices", "Peer review"]
    },
    {
      id: "bcm-coordination-service",
      name: "BCM Coordination Service",
      port: 8070,
      description: "Cross-service BCM coordination",
      techStack: ["Python 3.11", "FastAPI", "RabbitMQ"],
      dependencies: ["eventbus", "all-services"],
      apiEndpoints: 8,
      status: "active",
      features: ["Service orchestration", "Workflow coordination", "Status aggregation"]
    }
  ],
  "intelligent-core": [
    {
      id: "ai-foundation",
      name: "AI Foundation",
      port: 8040,
      description: "Core AI services: LLM routing, RAG pipeline, ML models",
      techStack: ["Python 3.11", "Claude API", "Qdrant", "scikit-learn"],
      dependencies: ["qdrant", "redis"],
      apiEndpoints: 20,
      status: "active",
      features: ["LLM routing", "RAG (<500ms)", "ML models (87% accuracy)", "Context management"]
    },
    {
      id: "workflow-intelligence",
      name: "Workflow Intelligence",
      port: 8037,
      description: "BPMN workflow engine with Temporal",
      techStack: ["Python 3.11", "Temporal", "BPMN 2.0", "PostgreSQL"],
      dependencies: ["temporal", "database"],
      apiEndpoints: 16,
      status: "active",
      features: ["BPMN execution", "Workflow monitoring", "Long-running processes", "Error recovery"]
    },
    {
      id: "expertise-center",
      name: "Expertise Center",
      port: 8035,
      description: "14 domain AI specialists",
      techStack: ["Python 3.11", "Claude API"],
      dependencies: ["ai-foundation", "collective"],
      apiEndpoints: 14,
      status: "active",
      features: ["14 specialists", "Domain expertise", "Multi-agent collaboration"]
    },
    {
      id: "predictive",
      name: "Predictive Intelligence",
      port: 8031,
      description: "Journey prediction and forecasting",
      techStack: ["Python 3.11", "scikit-learn", "Prophet"],
      dependencies: ["ai-foundation", "database"],
      apiEndpoints: 8,
      status: "active",
      features: ["Journey prediction", "Time series", "Anomaly detection"]
    },
    {
      id: "collective",
      name: "Collective Intelligence",
      port: 8032,
      description: "Anonymous collaboration and case library (347+ cases)",
      techStack: ["Python 3.11", "PostgreSQL", "k-anonymity"],
      dependencies: ["database"],
      apiEndpoints: 12,
      status: "active",
      features: ["347+ cases", "k-anonymity (k=5)", "Pattern recognition", "Best practices"]
    },
    {
      id: "community-intelligence",
      name: "Community Intelligence",
      port: 8030,
      description: "Peer learning and community insights",
      techStack: ["Python 3.11", "PostgreSQL"],
      dependencies: ["collective"],
      apiEndpoints: 10,
      status: "active",
      features: ["Peer review", "Community insights", "Q&A"]
    },
    {
      id: "event-intelligence",
      name: "Event Intelligence",
      port: 8039,
      description: "Auto-discovery and event pattern recognition",
      techStack: ["Python 3.11", "RabbitMQ", "Redis Streams"],
      dependencies: ["eventbus", "ai-foundation"],
      apiEndpoints: 8,
      status: "active",
      features: ["Auto-discovery", "Pattern recognition", "Anomaly detection", "Proactive alerts"]
    },
    {
      id: "ai-workflow-optimizer",
      name: "AI Workflow Optimizer",
      port: 8038,
      description: "ML-based workflow optimization",
      techStack: ["Python 3.11", "scikit-learn"],
      dependencies: ["workflow-intelligence", "ai-foundation"],
      apiEndpoints: 6,
      status: "active",
      features: ["Optimization", "Performance prediction", "Bottleneck detection"]
    },
    {
      id: "workflow-engine",
      name: "Workflow Engine",
      port: 8036,
      description: "BPMN 2.0 execution engine",
      techStack: ["Python 3.11", "BPMN 2.0"],
      dependencies: ["database"],
      apiEndpoints: 10,
      status: "active",
      features: ["BPMN execution", "State management", "Error handling"]
    },
    {
      id: "orchestration",
      name: "AI Orchestration",
      port: 8034,
      description: "Intent-to-API orchestration ('Super Brain')",
      techStack: ["Python 3.11", "Claude API"],
      dependencies: ["ai-foundation", "all-services"],
      apiEndpoints: 12,
      status: "active",
      features: ["Intent detection", "API routing", "Multi-step workflows", "Context management"]
    },
    {
      id: "system-bcm-service",
      name: "System BCM Service",
      port: 8050,
      description: "Platform self-application BCM service",
      techStack: ["Python 3.11", "FastAPI"],
      dependencies: ["all-services"],
      apiEndpoints: 7,
      status: "active",
      features: ["Platform BIA", "Auto-recovery (7 procedures)", "Practice learning", "Self-monitoring"]
    }
  ]
};

// Calculate totals
const allServices = [...services['platform-services'], ...services['intelligent-core']];
const totals = {
  totalServices: allServices.length,
  totalEndpoints: allServices.reduce((sum, s) => sum + s.apiEndpoints, 0),
  byStatus: {
    active: allServices.filter(s => s.status === 'active').length,
    development: allServices.filter(s => s.status === 'development').length,
  }
};

const output = {
  services: allServices,
  categories: services,
  totals,
  lastGenerated: new Date().toISOString()
};

const outputPath = path.join(__dirname, '../src/data/services.json');
fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));

console.log(`✅ Generated services.json: ${totals.totalServices} services, ${totals.totalEndpoints} endpoints`);
```

#### `scripts/generate-diagrams-data.js`

```javascript
const fs = require('fs');
const path = require('path');
const glob = require('glob');

const diagramsDir = path.join(__dirname, '../../doc-project/diagrams');
const categories = ['architecture', 'user-scenarios', 'dependencies', 'flows', 'integration', 'business-processes'];

const diagrams = [];

categories.forEach(category => {
  const files = glob.sync(`${diagramsDir}/${category}/*.mmd`);

  files.forEach(filePath => {
    const fileName = path.basename(filePath, '.mmd');
    const content = fs.readFileSync(filePath, 'utf8');

    // Extract diagram type
    const firstLine = content.split('\n')[0].trim();
    let diagramType = 'flowchart';
    if (firstLine.includes('sequenceDiagram')) diagramType = 'sequence';
    if (firstLine.includes('classDiagram')) diagramType = 'class';
    if (firstLine.includes('stateDiagram')) diagramType = 'state';
    if (firstLine.includes('erDiagram')) diagramType = 'er';
    if (firstLine.includes('gantt')) diagramType = 'gantt';

    diagrams.push({
      id: `${category}-${fileName}`.toLowerCase().replace(/_/g, '-'),
      title: fileName.replace(/_/g, ' '),
      category,
      file: `${category}/${fileName}.mmd`,
      type: diagramType,
      description: `${category} diagram: ${fileName}`,
      tags: [category, diagramType],
      lastUpdated: fs.statSync(filePath).mtime.toISOString().split('T')[0]
    });
  });
});

const output = {
  diagrams,
  totalCount: diagrams.length,
  byCategory: categories.reduce((acc, cat) => {
    acc[cat] = diagrams.filter(d => d.category === cat).length;
    return acc;
  }, {}),
  byType: {
    flowchart: diagrams.filter(d => d.type === 'flowchart').length,
    sequence: diagrams.filter(d => d.type === 'sequence').length,
    class: diagrams.filter(d => d.type === 'class').length,
  },
  lastGenerated: new Date().toISOString()
};

const outputPath = path.join(__dirname, '../src/data/diagrams.json');
fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));

console.log(`✅ Generated diagrams.json: ${diagrams.length} diagrams across ${categories.length} categories`);
```

---

### 4. React Components

#### `src/components/ServiceCard/index.tsx`

```typescript
import React from 'react';
import Link from '@docusaurus/Link';
import { FaServer, FaCode, FaBook } from 'react-icons/fa';
import styles from './styles.module.css';

interface ServiceCardProps {
  service: {
    id: string;
    name: string;
    port: number;
    description: string;
    techStack: string[];
    status: string;
    apiEndpoints: number;
  };
}

export default function ServiceCard({ service }: ServiceCardProps): JSX.Element {
  const statusColors = {
    active: 'success',
    development: 'warning',
    deprecated: 'danger'
  };

  return (
    <div className={styles.serviceCard}>
      <div className={styles.header}>
        <h3>{service.name}</h3>
        <span className={styles.portBadge}>:{service.port}</span>
        <span className={`badge badge--${statusColors[service.status]}`}>
          {service.status}
        </span>
      </div>

      <p className={styles.description}>{service.description}</p>

      <div className={styles.techStack}>
        {service.techStack.slice(0, 3).map(tech => (
          <span key={tech} className={styles.techBadge}>{tech}</span>
        ))}
        {service.techStack.length > 3 && (
          <span className={styles.techBadge}>+{service.techStack.length - 3}</span>
        )}
      </div>

      <div className={styles.footer}>
        <div className={styles.stats}>
          <span>📡 {service.apiEndpoints} endpoints</span>
        </div>
        <div className={styles.actions}>
          <Link to={`/services/${service.id}`} className="button button--primary button--sm">
            Details
          </Link>
        </div>
      </div>
    </div>
  );
}
```

#### `src/components/ServiceCard/styles.module.css`

```css
.serviceCard {
  border: 1px solid var(--ifm-color-emphasis-300);
  border-radius: 8px;
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.serviceCard:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.header h3 {
  margin: 0;
  font-size: 1.2rem;
  flex: 1;
}

.portBadge {
  background: var(--ifm-color-primary-lighter);
  color: var(--ifm-color-primary-darker);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.85rem;
}

.description {
  color: var(--ifm-color-emphasis-700);
  margin-bottom: 1rem;
  flex: 1;
}

.techStack {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.techBadge {
  background: var(--ifm-color-emphasis-200);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--ifm-color-emphasis-200);
}

.stats {
  font-size: 0.85rem;
  color: var(--ifm-color-emphasis-600);
}

.actions {
  display: flex;
  gap: 0.5rem;
}
```

---

### 5. Custom Pages

#### `src/pages/services.tsx`

```typescript
import React, { useState } from 'react';
import Layout from '@theme/Layout';
import ServiceCard from '@site/src/components/ServiceCard';
import servicesData from '@site/src/data/services.json';

export default function ServicesPage(): JSX.Element {
  const [filter, setFilter] = useState<string>('all');
  const [search, setSearch] = useState<string>('');

  const filteredServices = servicesData.services.filter(service => {
    const matchesFilter = filter === 'all' ||
      (filter === 'platform' && service.id.includes('service')) ||
      (filter === 'intelligent' && !service.id.includes('service'));

    const matchesSearch = search === '' ||
      service.name.toLowerCase().includes(search.toLowerCase()) ||
      service.description.toLowerCase().includes(search.toLowerCase());

    return matchesFilter && matchesSearch;
  });

  return (
    <Layout
      title="Services Catalog"
      description="Explore all 23 services of AI-Platform-ISO">
      <div className="container margin-vert--lg">
        <h1>Services Catalog</h1>
        <p>Platform comprises <strong>{servicesData.totals.totalServices} services</strong> with <strong>{servicesData.totals.totalEndpoints} API endpoints</strong></p>

        <div style={{ marginBottom: '2rem' }}>
          <input
            type="text"
            placeholder="Search services..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid var(--ifm-color-emphasis-300)',
              borderRadius: '4px',
              marginBottom: '1rem'
            }}
          />

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button
              onClick={() => setFilter('all')}
              className={`button ${filter === 'all' ? 'button--primary' : 'button--secondary'}`}>
              All ({servicesData.totals.totalServices})
            </button>
            <button
              onClick={() => setFilter('platform')}
              className={`button ${filter === 'platform' ? 'button--primary' : 'button--secondary'}`}>
              Platform Services (12)
            </button>
            <button
              onClick={() => setFilter('intelligent')}
              className={`button ${filter === 'intelligent' ? 'button--primary' : 'button--secondary'}`}>
              Intelligent Core (11)
            </button>
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
          gap: '1.5rem'
        }}>
          {filteredServices.map(service => (
            <ServiceCard key={service.id} service={service} />
          ))}
        </div>

        {filteredServices.length === 0 && (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <p>No services found matching your criteria.</p>
          </div>
        )}
      </div>
    </Layout>
  );
}
```

---

## Deployment Steps

### 1. Prerequisites

```bash
# Install Node.js 18+
node --version  # Should be >= 18.0.0

# Install dependencies
cd docs-website
npm install
```

### 2. Generate Data

```bash
npm run generate-data
```

### 3. Local Development

```bash
npm start
# Open http://localhost:3000
```

### 4. Build for Production

```bash
npm run build
# Output: build/
```

### 5. Deploy to GitHub Pages

```bash
# Option 1: Manual
npm run deploy

# Option 2: GitHub Actions (automatic)
# Push to main branch, GitHub Actions will deploy
git add .
git commit -m "feat: add documentation website"
git push origin main
```

---

## Timeline

| Week | Tasks |
|------|-------|
| 1 | Setup Docusaurus, create basic structure, generate data files |
| 2 | Build service catalog page, implement search |
| 3 | Create diagram viewer with Mermaid integration |
| 4 | Build document library with filters |
| 5 | Implement API reference with Swagger UI |
| 6 | Add interactive features, polish UI |
| 7 | Testing, performance optimization |
| 8 | Documentation, deployment, launch |

---

## Next Steps

1. ✅ Run `npx create-docusaurus@latest . classic --typescript`
2. ✅ Copy files from this guide
3. ✅ Run `npm run generate-data`
4. ✅ Run `npm start` to preview
5. ✅ Customize branding (logo, colors)
6. ✅ Deploy to GitHub Pages

---

**Status**: Ready for Implementation
**Estimated Effort**: 8 weeks (1 developer)
**Technologies**: Docusaurus, React, TypeScript, Mermaid.js
