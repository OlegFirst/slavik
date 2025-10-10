import Link from 'next/link'
import { FileText, GitBranch, Settings, FileCode, BarChart3, BookOpen } from 'lucide-react'
import { getAllDocs } from '@/lib/docs'

export default function HomePage() {
  const docs = getAllDocs()
  const categories = {
    architecture: docs.filter(d => d.category === 'architecture').length,
    requirements: docs.filter(d => d.category === 'requirements').length,
    design: docs.filter(d => d.category === 'design').length,
    implementation: docs.filter(d => d.category === 'implementation').length,
    reports: docs.filter(d => d.category === 'reports').length,
  }

  const features = [
    {
      icon: FileText,
      title: 'Architecture',
      description: 'Complete system architecture documentation with diagrams and specifications',
      count: categories.architecture,
      href: '/docs/architecture',
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-950',
    },
    {
      icon: GitBranch,
      title: 'Requirements',
      description: 'Detailed requirements specifications and user segment documentation',
      count: categories.requirements,
      href: '/docs/requirements',
      color: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-50 dark:bg-purple-950',
    },
    {
      icon: Settings,
      title: 'Design',
      description: 'Technical design documents and system specifications',
      count: categories.design,
      href: '/docs/design',
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-950',
    },
    {
      icon: FileCode,
      title: 'Implementation',
      description: 'Implementation guides, integration patterns, and deployment instructions',
      count: categories.implementation,
      href: '/docs/implementation',
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-50 dark:bg-orange-950',
    },
    {
      icon: BarChart3,
      title: 'Reports',
      description: 'Progress reports, audits, and compliance documentation',
      count: categories.reports,
      href: '/docs/reports',
      color: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-red-50 dark:bg-red-950',
    },
  ]

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Hero Section */}
      <div className="mb-12 text-center">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
          AI-Platform-ISO
        </h1>
        <p className="text-xl text-muted-foreground mb-6 max-w-3xl mx-auto">
          Professional technical documentation for Business Continuity Management Platform with AI Intelligence and ISO 22301 Compliance
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Link
            href="/docs/ARCHITECTURE"
            className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors font-medium"
          >
            <BookOpen className="w-5 h-5" />
            Get Started
          </Link>
          <Link
            href="/search"
            className="inline-flex items-center gap-2 bg-secondary text-secondary-foreground px-6 py-3 rounded-lg hover:bg-secondary/80 transition-colors font-medium"
          >
            Search Documentation
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
        <div className="bg-card border rounded-lg p-6 text-center">
          <div className="text-4xl font-bold text-primary mb-2">{docs.length}</div>
          <div className="text-muted-foreground">Total Documents</div>
        </div>
        <div className="bg-card border rounded-lg p-6 text-center">
          <div className="text-4xl font-bold text-primary mb-2">5</div>
          <div className="text-muted-foreground">Categories</div>
        </div>
        <div className="bg-card border rounded-lg p-6 text-center">
          <div className="text-4xl font-bold text-primary mb-2">100%</div>
          <div className="text-muted-foreground">Production Ready</div>
        </div>
      </div>

      {/* Category Cards */}
      <div className="mb-12">
        <h2 className="text-3xl font-bold mb-6">Documentation Categories</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => {
            const Icon = feature.icon
            return (
              <Link
                key={feature.title}
                href={feature.href}
                className="block group"
              >
                <div className="h-full bg-card border rounded-lg p-6 hover:shadow-lg transition-all hover:border-primary">
                  <div className={`w-12 h-12 rounded-lg ${feature.bgColor} flex items-center justify-center mb-4`}>
                    <Icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground mb-4 text-sm">
                    {feature.description}
                  </p>
                  <div className="flex items-center gap-2 text-sm text-primary font-medium">
                    <span>{feature.count} documents</span>
                    <span className="group-hover:translate-x-1 transition-transform">→</span>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      </div>

      {/* Recent Documents */}
      <div>
        <h2 className="text-3xl font-bold mb-6">Recent Documents</h2>
        <div className="space-y-4">
          {docs.slice(0, 6).map((doc) => (
            <Link
              key={doc.slug}
              href={`/docs/${doc.slug}`}
              className="block bg-card border rounded-lg p-4 hover:shadow-md transition-all hover:border-primary"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-1 hover:text-primary transition-colors">
                    {doc.title}
                  </h3>
                  {doc.description && (
                    <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                      {doc.description}
                    </p>
                  )}
                  <div className="flex gap-2 flex-wrap">
                    <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded">
                      {doc.category}
                    </span>
                    {doc.tags && doc.tags.slice(0, 3).map((tag) => (
                      <span key={tag} className="text-xs px-2 py-1 bg-muted text-muted-foreground rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <FileText className="w-8 h-8 text-muted-foreground ml-4 flex-shrink-0" />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
