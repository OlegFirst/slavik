import Link from 'next/link'
import { ChevronRight } from 'lucide-react'

interface BreadcrumbsProps {
  slug: string
}

export function Breadcrumbs({ slug }: BreadcrumbsProps) {
  const segments = slug.split('/')
  const breadcrumbs = segments.map((segment, index) => {
    const href = '/docs/' + segments.slice(0, index + 1).join('/')
    const label = segment
      .replace(/_/g, ' ')
      .replace(/-/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')

    return { href, label, isLast: index === segments.length - 1 }
  })

  return (
    <nav className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
      <Link href="/" className="hover:text-foreground transition-colors">
        Home
      </Link>
      <ChevronRight className="w-4 h-4" />
      <Link href="/docs" className="hover:text-foreground transition-colors">
        Docs
      </Link>
      {breadcrumbs.map((crumb, index) => (
        <div key={index} className="flex items-center gap-2">
          <ChevronRight className="w-4 h-4" />
          {crumb.isLast ? (
            <span className="text-foreground font-medium">{crumb.label}</span>
          ) : (
            <Link href={crumb.href} className="hover:text-foreground transition-colors">
              {crumb.label}
            </Link>
          )}
        </div>
      ))}
    </nav>
  )
}
