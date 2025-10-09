import React, { useState } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './index.module.css';

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  const [view, setView] = useState<'business' | 'technical'>('business');

  return (
    <Layout
      title={`${siteConfig.title} - Home`}
      description="Business Continuity Management Platform with AI Intelligence">

      {/* Hero Section */}
      <header className={styles.heroBanner}>
        <div className="container">
          <h1 className="hero__title">{siteConfig.title}</h1>
          <p className="hero__subtitle">{siteConfig.tagline}</p>

          {/* View Toggle */}
          <div className={styles.viewToggle}>
            <button
              className={`button ${view === 'business' ? 'button--primary' : 'button--secondary'}`}
              onClick={() => setView('business')}>
              👔 Business View
            </button>
            <button
              className={`button ${view === 'technical' ? 'button--primary' : 'button--secondary'}`}
              onClick={() => setView('technical')}>
              💻 Technical View
            </button>
          </div>

          <div className={styles.buttons}>
            <Link
              className="button button--primary button--lg"
              to="/for-partners">
              For Partners & Stakeholders
            </Link>
            <Link
              className="button button--secondary button--lg"
              to="/docs/intro">
              Technical Documentation
            </Link>
          </div>
        </div>
      </header>

      <main>
        {view === 'business' ? <BusinessView /> : <TechnicalView />}
      </main>
    </Layout>
  );
}

function BusinessView(): JSX.Element {
  const businessFeatures = [
    {
      icon: '🎯',
      title: 'BCM Journey Guide',
      description: 'Visual timeline with AI recommendations. Know where you are, what\'s next, and when you\'ll finish.',
      benefits: '70% faster completion'
    },
    {
      icon: '📊',
      title: 'Business Impact Analysis',
      description: '6-step wizard with AI auto-discovery. Identify critical processes and dependencies.',
      benefits: '30% more dependencies found'
    },
    {
      icon: '⚠️',
      title: 'Risk Management',
      description: 'AI-powered risk assessment from 347+ cases. Risk heatmap, treatment plans, and recommendations.',
      benefits: 'Data-driven decisions'
    },
    {
      icon: '📋',
      title: 'BC Plans',
      description: 'Create plans in 3 ways: templates (30 min), AI-generated (10 min), or from scratch.',
      benefits: '80% faster plan creation'
    },
    {
      icon: '🎲',
      title: 'Digital Twin Testing',
      description: 'Test BC plans without disruption. Unique feature - only BCM platform with Digital Twin.',
      benefits: 'Test without downtime'
    },
    {
      icon: '✓',
      title: 'ISO 22301 Compliance',
      description: 'Real-time compliance dashboard. Track all 10 clauses, gap analysis, evidence library.',
      benefits: '50% faster certification'
    },
  ];

  return (
    <section className={styles.features}>
      <div className="container">
        <h2 className="text--center margin-bottom--lg">What AI-Platform-ISO Does For You</h2>

        {/* Key Metrics */}
        <div className={styles.metrics}>
          <div className={styles.metricCard}>
            <div className={styles.metricValue}>70%</div>
            <div className={styles.metricLabel}>Faster BIA</div>
          </div>
          <div className={styles.metricCard}>
            <div className={styles.metricValue}>80%</div>
            <div className={styles.metricLabel}>Faster BC Plans</div>
          </div>
          <div className={styles.metricCard}>
            <div className={styles.metricValue}>347+</div>
            <div className={styles.metricLabel}>Real Cases</div>
          </div>
          <div className={styles.metricCard}>
            <div className={styles.metricValue}>500%</div>
            <div className={styles.metricLabel}>ROI Year 1</div>
          </div>
        </div>

        {/* Features Grid */}
        <div className={styles.featuresGrid}>
          {businessFeatures.map((feature, idx) => (
            <div key={idx} className={styles.featureCard}>
              <div className={styles.featureIcon}>{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
              <div className={styles.featureBenefit}>
                <strong>✅ {feature.benefits}</strong>
              </div>
            </div>
          ))}
        </div>

        {/* Success Story */}
        <div className={styles.successStory}>
          <h3>🎯 Success Story: Healthcare Provider</h3>
          <div className={styles.storyContent}>
            <p>
              <strong>Challenge:</strong> 5000-employee healthcare provider needed ISO 22301 for insurance contracts.
            </p>
            <p>
              <strong>Results:</strong>
            </p>
            <ul>
              <li>✅ Achieved ISO 22301 certification in 8 months (vs 18 months average)</li>
              <li>💰 Saved $300K in consulting costs</li>
              <li>📈 Won $5M contract requiring ISO 22301</li>
            </ul>
          </div>
        </div>

        {/* CTA */}
        <div className="text--center margin-top--lg">
          <Link
            className="button button--primary button--lg"
            to="/for-partners">
            See All Business Features →
          </Link>
        </div>
      </div>
    </section>
  );
}

function TechnicalView(): JSX.Element {
  const technicalFeatures = [
    {
      icon: '🏗️',
      title: '23 Microservices',
      description: '12 platform services + 11 intelligent core modules with 150+ API endpoints',
      link: '/services'
    },
    {
      icon: '🤖',
      title: 'AI Foundation',
      description: 'LLM routing, RAG pipeline (<500ms), ML models (87% accuracy), 14 domain specialists',
      link: '/docs/ai-foundation'
    },
    {
      icon: '🔄',
      title: 'Event-Driven Architecture',
      description: 'EventBus with Redis Streams + RabbitMQ. Auto-discovery and pattern recognition.',
      link: '/docs/architecture/eventbus'
    },
    {
      icon: '📊',
      title: '36 Architecture Diagrams',
      description: 'Interactive Mermaid diagrams covering architecture, flows, dependencies, and user scenarios',
      link: '/diagrams'
    },
    {
      icon: '📚',
      title: '550+ Documents',
      description: 'Complete documentation library with full-text search and specifications catalog',
      link: '/library'
    },
    {
      icon: '🔌',
      title: 'REST & GraphQL APIs',
      description: '150+ endpoints with OpenAPI/AsyncAPI specs, Swagger UI, and interactive testing',
      link: '/api'
    },
  ];

  return (
    <section className={styles.features}>
      <div className="container">
        <h2 className="text--center margin-bottom--lg">Technical Platform Overview</h2>

        {/* Tech Stack */}
        <div className={styles.techStack}>
          <div className={styles.techCategory}>
            <h4>Backend</h4>
            <div className={styles.techTags}>
              <span>Python 3.11</span>
              <span>FastAPI</span>
              <span>PostgreSQL</span>
              <span>Redis</span>
              <span>RabbitMQ</span>
            </div>
          </div>
          <div className={styles.techCategory}>
            <h4>AI/ML</h4>
            <div className={styles.techTags}>
              <span>Claude API</span>
              <span>Qdrant</span>
              <span>scikit-learn</span>
              <span>Temporal</span>
            </div>
          </div>
          <div className={styles.techCategory}>
            <h4>Frontend</h4>
            <div className={styles.techTags}>
              <span>Next.js 14</span>
              <span>TypeScript</span>
              <span>Tailwind CSS</span>
              <span>Zustand</span>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className={styles.featuresGrid}>
          {technicalFeatures.map((feature, idx) => (
            <div key={idx} className={styles.featureCard}>
              <div className={styles.featureIcon}>{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
              <Link to={feature.link} className="button button--secondary button--sm">
                Explore →
              </Link>
            </div>
          ))}
        </div>

        {/* Architecture Highlights */}
        <div className={styles.architectureHighlight}>
          <h3>🏗️ 4-Layer Architecture</h3>
          <div className={styles.layersGrid}>
            <div className={styles.layer}>
              <h4>Layer 1: Infrastructure</h4>
              <p>EventBus, Database, Cache, Vector DB, Message Queue</p>
            </div>
            <div className={styles.layer}>
              <h4>Layer 2: Intelligent Core</h4>
              <p>11 AI modules including ai-foundation, workflow-intelligence, expertise-center</p>
            </div>
            <div className={styles.layer}>
              <h4>Layer 3: Platform Services</h4>
              <p>12 business services: BIA, Risk, Compliance, Plans, etc.</p>
            </div>
            <div className={styles.layer}>
              <h4>Layer 4: Integration</h4>
              <p>REST APIs, GraphQL, WebSockets, External integrations</p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text--center margin-top--lg">
          <Link
            className="button button--primary button--lg"
            to="/docs/architecture/overview">
            View Full Architecture →
          </Link>
        </div>
      </div>
    </section>
  );
}
