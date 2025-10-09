import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './for-partners.module.css';

export default function ForPartnersPage(): JSX.Element {
  return (
    <Layout
      title="For Partners & Stakeholders"
      description="What AI-Platform-ISO does for your business">

      {/* Hero */}
      <header className={styles.hero}>
        <div className="container">
          <h1>AI-Platform-ISO for Partners & Stakeholders</h1>
          <p className={styles.subtitle}>
            Understand what the platform does for users — not how it's built
          </p>
        </div>
      </header>

      <main className="container margin-vert--lg">

        {/* What Is Section */}
        <section className={styles.section}>
          <h2>🎯 What is AI-Platform-ISO?</h2>
          <p className={styles.intro}>
            <strong>AI-Platform-ISO</strong> is an intelligent Business Continuity Management (BCM) platform that helps organizations:
          </p>
          <div className={styles.benefitsGrid}>
            <div className={styles.benefit}>✅ Achieve ISO 22301 compliance</div>
            <div className={styles.benefit}>✅ Protect critical business operations</div>
            <div className={styles.benefit}>✅ Recover faster from disruptions</div>
            <div className={styles.benefit}>✅ Learn from 347+ real-world cases</div>
            <div className={styles.benefit}>✅ Make data-driven BCM decisions with AI</div>
          </div>
          <p className={styles.targetAudience}>
            <strong>For whom:</strong> Companies that need business continuity, disaster recovery, and ISO 22301 certification.
          </p>
        </section>

        {/* Key Functions */}
        <section className={styles.section}>
          <h2>💼 10 Key Business Functions</h2>

          {keyFunctions.map((func, idx) => (
            <div key={idx} className={styles.functionCard}>
              <div className={styles.functionHeader}>
                <span className={styles.functionIcon}>{func.icon}</span>
                <h3>{func.title}</h3>
              </div>
              <p className={styles.functionDesc}>{func.description}</p>

              {func.features && (
                <div className={styles.featuresList}>
                  <strong>Key Features:</strong>
                  <ul>
                    {func.features.map((feature, i) => (
                      <li key={i}>{feature}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className={styles.businessValue}>
                <strong>💡 Business Value:</strong> {func.businessValue}
              </div>

              {func.timeSavings && (
                <div className={styles.metric}>
                  <strong>⏱️ Time Savings:</strong> {func.timeSavings}
                </div>
              )}

              {func.example && (
                <div className={styles.example}>
                  <strong>📖 Example:</strong> {func.example}
                </div>
              )}
            </div>
          ))}
        </section>

        {/* Business Outcomes */}
        <section className={styles.section}>
          <h2>🎯 Business Outcomes (Real Metrics)</h2>

          <div className={styles.outcomesGrid}>
            <div className={styles.outcomeCategory}>
              <h3>⏱️ Time Savings</h3>
              <ul>
                <li><strong>BIA:</strong> 70% faster (2 weeks vs 6 weeks)</li>
                <li><strong>BC Plans:</strong> 80% faster (hours vs days)</li>
                <li><strong>Risk Assessment:</strong> 60% faster</li>
                <li><strong>ISO Certification:</strong> 50% faster (8 vs 18 months)</li>
              </ul>
            </div>

            <div className={styles.outcomeCategory}>
              <h3>💰 Cost Savings</h3>
              <ul>
                <li><strong>Consulting:</strong> 40% reduction</li>
                <li><strong>Training:</strong> 60% reduction</li>
                <li><strong>Audit:</strong> 30% reduction</li>
              </ul>
            </div>

            <div className={styles.outcomeCategory}>
              <h3>🎯 Quality Improvements</h3>
              <ul>
                <li><strong>Dependencies:</strong> 30% more found</li>
                <li><strong>Gaps:</strong> 25% more detected</li>
                <li><strong>Plan Quality:</strong> 40% fewer defects</li>
              </ul>
            </div>

            <div className={styles.outcomeCategory}>
              <h3>⚠️ Risk Reduction</h3>
              <ul>
                <li><strong>Recovery:</strong> 50% faster RTO</li>
                <li><strong>Incidents:</strong> 35% reduction</li>
                <li><strong>Preparedness:</strong> 90% exercise success</li>
              </ul>
            </div>
          </div>
        </section>

        {/* ROI Calculator */}
        <section className={styles.section}>
          <h2>📊 ROI Example (Mid-Market Company)</h2>
          <p>Typical company: 1000 employees, $100M revenue</p>

          <div className={styles.roiGrid}>
            <div className={styles.roiCard}>
              <h3>Costs (Year 1)</h3>
              <ul>
                <li>Platform License: $50,000</li>
                <li>Implementation: $20,000</li>
                <li>Training: $10,000</li>
              </ul>
              <div className={styles.roiTotal}>Total: $80,000</div>
            </div>

            <div className={styles.roiCard}>
              <h3>Savings (Year 1)</h3>
              <ul>
                <li>Consulting Reduction: $150,000</li>
                <li>Faster Certification: $100,000</li>
                <li>Reduced Training: $30,000</li>
                <li>Incident Prevention: $200,000</li>
              </ul>
              <div className={styles.roiTotal}>Total: $480,000</div>
            </div>
          </div>

          <div className={styles.roiResult}>
            <h3>Net ROI Year 1: $400,000</h3>
            <p className={styles.roiPercent}>500% ROI</p>
          </div>
        </section>

        {/* Success Stories */}
        <section className={styles.section}>
          <h2>🎯 Success Stories</h2>

          {successStories.map((story, idx) => (
            <div key={idx} className={styles.storyCard}>
              <h3>{story.title}</h3>
              <p><strong>Challenge:</strong> {story.challenge}</p>
              <p><strong>Solution:</strong> {story.solution}</p>
              <div className={styles.storyResults}>
                <strong>Results:</strong>
                <ul>
                  {story.results.map((result, i) => (
                    <li key={i}>{result}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </section>

        {/* Unique Differentiators */}
        <section className={styles.section}>
          <h2>💡 What Makes Us Unique</h2>

          <div className={styles.differentiatorsGrid}>
            {differentiators.map((diff, idx) => (
              <div key={idx} className={styles.differentiatorCard}>
                <h3>{diff.title}</h3>
                <p>{diff.description}</p>
                <ul>
                  {diff.points.map((point, i) => (
                    <li key={i}>{point}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className={styles.ctaSection}>
          <h2>🚀 Ready to Get Started?</h2>
          <div className={styles.ctaButtons}>
            <Link
              className="button button--primary button--lg"
              to="mailto:partners@yourplatform.com">
              Contact Sales
            </Link>
            <Link
              className="button button--secondary button--lg"
              to="/docs/intro">
              View Technical Docs
            </Link>
          </div>
        </section>

      </main>
    </Layout>
  );
}

const keyFunctions = [
  {
    icon: '🎯',
    title: 'BCM Journey Guide',
    description: 'Guides organizations through the complete BCM journey from start to finish.',
    features: [
      'Visual timeline showing current progress',
      'AI recommends next steps',
      'Predicts completion time',
      'Red flags if falling behind'
    ],
    businessValue: 'Clients see clear progress → higher satisfaction, predictable timelines → better project planning',
    timeSavings: 'Automated guidance reduces consulting hours',
    example: 'A manufacturing company completed their BCM program in 6 months instead of 12, because AI predicted bottlenecks.'
  },
  {
    icon: '📊',
    title: 'Business Impact Analysis (BIA)',
    description: 'Identifies critical business processes and their dependencies with 6-step wizard.',
    features: [
      'AI suggests critical processes based on industry',
      'Auto-discovers hidden dependencies',
      'Calculates financial impact ($50K/hour downtime)',
      'Recommends optimal RTO/RPO'
    ],
    businessValue: 'AI catches 30% more dependencies than manual analysis, automated data collection reduces costs',
    timeSavings: '70% faster (2 weeks vs 6 weeks)',
    example: 'A hospital discovered patient records depended on 3rd-party email with no SLA. Fixed before incident.'
  },
  {
    icon: '⚠️',
    title: 'Risk Management',
    description: 'Identifies, assesses, and manages BCM-related risks with AI recommendations.',
    features: [
      'Risk heatmap (5×5 matrix)',
      'AI recommendations from 347+ cases',
      'Auto-generate treatment plans',
      'Track progress'
    ],
    businessValue: 'Data-driven risk assessment (not gut feel), instant mitigation suggestions, learn from 347+ cases',
    example: 'Retail company identified ransomware risk. AI suggested mitigation from 23 similar companies. Avoided $2M attack.'
  },
  {
    icon: '📋',
    title: 'Business Continuity Plans',
    description: 'Creates, manages, and tests BC plans in 3 ways: templates (30 min), AI-generated (10 min), or from scratch.',
    features: [
      'Pre-built templates auto-populated from BIA',
      'AI generates complete plans',
      'Version control and approval workflow',
      'Mobile access during incidents'
    ],
    businessValue: 'AI ensures all ISO 22301 requirements covered, auto-updates when business changes',
    timeSavings: '80% faster (hours vs days)',
    example: 'Financial services company needed 15 plans. AI generated all in 2 hours vs 3 weeks manual.'
  },
  {
    icon: '🎲',
    title: 'Digital Twin Testing',
    description: 'Tests BC plans without disrupting business. Only BCM platform with Digital Twin simulation.',
    features: [
      'Virtual environment (exact copy of IT systems)',
      'Inject failure scenarios',
      'Measure actual RTO',
      'AI insights on gaps'
    ],
    businessValue: 'Test without downtime, discover issues before real incidents, prove compliance to auditors',
    example: 'E-commerce company found missing firewall rule in Digital Twin exercise. Fixed before Black Friday, saved $5M.'
  },
  {
    icon: '✓',
    title: 'ISO 22301 Compliance Dashboard',
    description: 'Tracks compliance with ISO 22301 standard in real-time.',
    features: [
      'Overall score 0-100% (color-coded)',
      'Clause-by-clause tracking',
      'AI gap detection',
      'Evidence library'
    ],
    businessValue: 'Know exactly where you stand, AI guides to gaps, all evidence organized for auditors',
    timeSavings: '50% faster certification (8 vs 18 months)',
    example: 'Healthcare provider achieved certification in 8 months. AI gap analysis saved 3 months of work.'
  },
  {
    icon: '📄',
    title: 'Document Management',
    description: 'Centralized repository for all BCM documents with smart organization.',
    features: [
      'AI auto-categorization',
      'Full-text search',
      'Version control',
      'Approval workflow'
    ],
    businessValue: 'No more "where is that document?", version control + approvals, complete audit trail',
  },
  {
    icon: '📈',
    title: 'Real-Time Monitoring & Analytics',
    description: 'Dashboards showing BCM program health for executives.',
    features: [
      'Journey progress chart with AI forecast',
      'Risk trends over time',
      'Compliance score tracking',
      'Exercise metrics'
    ],
    businessValue: 'Executives see status at a glance, make data-driven decisions, spot issues early',
  },
  {
    icon: '🎓',
    title: 'Community & Learning',
    description: 'Learn from 347+ anonymized real-world BCM cases.',
    features: [
      'Forums and Q&A',
      'Video courses and certifications',
      'Search 347+ cases by industry/challenge',
      'Best practices library (ISO, WHO, NIST)'
    ],
    businessValue: 'Don\'t reinvent the wheel, see how others solved similar problems, avoid mistakes',
    example: 'Logistics company found 12 similar supply chain cases, implemented best practices, recovered 50% faster.'
  },
  {
    icon: '🤖',
    title: 'AI Assistant',
    description: 'AI chatbot available on every screen for instant help.',
    features: [
      'Answer questions instantly',
      'Guided workflows',
      'Personalized recommendations',
      'Generate content (plans, policies)'
    ],
    businessValue: 'Instant help without waiting for support, users solve own problems, AI teaches users',
  },
];

const successStories = [
  {
    title: '🏥 Healthcare Provider (5000 employees)',
    challenge: 'Needed ISO 22301 for insurance contracts',
    solution: 'Used platform for 8 months',
    results: [
      '✅ Achieved ISO 22301 certification',
      '⏱️ 10 months faster than industry average',
      '💰 Saved $300K in consulting costs',
      '📈 Won $5M contract (required ISO 22301)'
    ]
  },
  {
    title: '💰 Financial Services (800 employees)',
    challenge: 'Ransomware risk, needed better preparedness',
    solution: 'Used Digital Twin for testing',
    results: [
      '✅ Discovered 12 gaps in BC plans',
      '✅ Fixed all gaps before real incident',
      '🔥 Survived ransomware with 2-hour downtime (vs 2-week average)',
      '💰 Saved estimated $2M in downtime costs'
    ]
  },
  {
    title: '🏭 Manufacturer (2000 employees)',
    challenge: 'Complex supply chain, many dependencies',
    solution: 'AI-powered BIA',
    results: [
      '✅ Found 30% more dependencies than manual BIA',
      '✅ Identified single-point-of-failure supplier',
      '✅ Diversified suppliers before disruption',
      '💰 Avoided $1M supply chain disruption'
    ]
  }
];

const differentiators = [
  {
    title: '🤖 Real AI (Not Buzzword)',
    description: 'Genuine AI recommendations from real-world data',
    points: [
      '347+ anonymized cases',
      '14 domain AI specialists',
      '87% ML model accuracy',
      'RAG queries <500ms'
    ]
  },
  {
    title: '🎮 Digital Twin Testing',
    description: 'Only BCM platform with Digital Twin simulation',
    points: [
      'Test without downtime',
      'Measure actual RTO',
      'Find gaps before incidents',
      'Saves $$$'
    ]
  },
  {
    title: '🏗️ Complete Platform',
    description: 'Not a point solution — end-to-end BCM journey',
    points: [
      'BIA → Risk → Plans → Exercises → Compliance',
      'No need for multiple tools',
      'All data connected',
      'Single source of truth'
    ]
  },
  {
    title: '📚 Learn from 347+ Cases',
    description: 'Largest anonymized BCM case library',
    points: [
      'Privacy-preserving (k-anonymity)',
      'Real-world proven solutions',
      'Search by industry/challenge',
      'Avoid common mistakes'
    ]
  }
];
