'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { FileText, GitBranch, Settings, FileCode, BarChart3, Home, X } from 'lucide-react'
import { getAllDocs } from '@/lib/docs'
import { useMemo } from 'react'
import clsx from 'clsx'

export function Sidebar() {
  const pathname = usePathname()
  const docs = useMemo(() => getAllDocs(), [])

  const categories = [
    {
      name: 'Architecture',
      icon: FileText,
      href: '/docs/architecture',
      docs: docs.filter(d => d.category === 'architecture'),
    },
    {
      name: 'Requirements',
      icon: GitBranch,
      href: '/docs/requirements',
      docs: docs.filter(d => d.category === 'requirements'),
    },
    {
      name: 'Design',
      icon: Settings,
      href: '/docs/design',
      docs: docs.filter(d => d.category === 'design'),
    },
    {
      name: 'Implementation',
      icon: FileCode,
      href: '/docs/implementation',
      docs: docs.filter(d => d.category === 'implementation'),
    },
    {
      name: 'Reports',
      icon: BarChart3,
      href: '/docs/reports',
      docs: docs.filter(d => d.category === 'reports'),
    },
  ]

  const closeSidebar = () => {
    const sidebar = document.getElementById('sidebar')
    if (sidebar && window.innerWidth < 1024) {
      sidebar.classList.add('-translate-x-full')
    }
  }

  return (
    <>
      {/* Overlay for mobile */}
      <div
        className="fixed inset-0 bg-black/50 z-40 lg:hidden"
        id="sidebar-overlay"
        onClick={closeSidebar}
        style={{ display: 'none' }}
      />

      {/* Sidebar */}
      <aside
        id="sidebar"
        className="fixed lg:sticky top-0 left-0 z-50 h-screen w-64 border-r bg-background transition-transform -translate-x-full lg:translate-x-0"
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-4 border-b">
            <Link href="/" className="font-bold text-lg" onClick={closeSidebar}>
              AI-Platform-ISO
            </Link>
            <button
              className="lg:hidden p-2 hover:bg-accent rounded-md"
              onClick={closeSidebar}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-1 mb-6">
              <Link
                href="/"
                onClick={closeSidebar}
                className={clsx(
                  'flex items-center gap-3 px-3 py-2 rounded-md transition-colors',
                  pathname === '/'
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent'
                )}
              >
                <Home className="w-4 h-4" />
                <span className="font-medium">Home</span>
              </Link>
            </div>

            {/* Categories */}
            {categories.map((category) => {
              const Icon = category.icon
              const isExpanded = pathname?.startsWith(`/docs/${category.name.toLowerCase()}`)

              return (
                <div key={category.name} className="mb-4">
                  <div className="flex items-center gap-2 px-3 py-2 text-sm font-semibold text-muted-foreground">
                    <Icon className="w-4 h-4" />
                    <span>{category.name}</span>
                    <span className="ml-auto text-xs bg-muted px-2 py-0.5 rounded">
                      {category.docs.length}
                    </span>
                  </div>
                  <div className="ml-6 space-y-1 mt-2">
                    {category.docs.slice(0, isExpanded ? undefined : 5).map((doc) => (
                      <Link
                        key={doc.slug}
                        href={`/docs/${doc.slug}`}
                        onClick={closeSidebar}
                        className={clsx(
                          'block px-3 py-1.5 text-sm rounded-md transition-colors',
                          pathname === `/docs/${doc.slug}`
                            ? 'bg-primary/10 text-primary font-medium'
                            : 'hover:bg-accent text-muted-foreground hover:text-foreground'
                        )}
                      >
                        <span className="line-clamp-1">{doc.title}</span>
                      </Link>
                    ))}
                    {!isExpanded && category.docs.length > 5 && (
                      <Link
                        href={`/docs/${category.name.toLowerCase()}`}
                        onClick={closeSidebar}
                        className="block px-3 py-1.5 text-sm text-primary hover:underline"
                      >
                        View all {category.docs.length} →
                      </Link>
                    )}
                  </div>
                </div>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t text-xs text-muted-foreground">
            <p>AI-Platform-ISO v1.0</p>
            <p className="mt-1">© 2025 All rights reserved</p>
          </div>
        </div>
      </aside>
    </>
  )
}
